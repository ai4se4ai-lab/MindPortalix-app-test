---
name: performance-profiling
description: >
  Use this skill whenever the user wants to diagnose or fix a performance
  problem — "this is slow", "why is this taking so long", "optimize this
  function", "reduce memory usage", "this endpoint has high latency", or
  any request to profile, benchmark, or speed up code. Also apply
  proactively before making optimization changes to any code the user
  hasn't already profiled — the skill's core rule is measure-first, so
  it should trigger even when the user jumps straight to "make this
  faster" without profiling data in hand. Covers methodology for finding
  and verifying bottlenecks (CPU, memory, I/O, network) across languages,
  with concrete tool commands for Python, Node.js, and general
  black-box benchmarking. Do NOT use this for algorithmic complexity
  questions asked in the abstract (e.g. "what's the Big-O of quicksort")
  with no actual code/system to profile, and do NOT use it for general
  code-quality review — see code-review-checklist for that.
location: /skills/performance-profiling.md
---

# Performance Profiling

The single biggest failure mode in performance work is optimizing based on
intuition instead of measurement. Intuition about hot paths is wrong far
more often than people expect. Every step below exists to replace a guess
with a number.

## 0. The methodology (apply in this order, every time)

1. **Define "slow."** Get a concrete target: current latency/time/memory
   vs. what's acceptable. "Make it faster" with no number invites
   over-optimizing the wrong thing. If the user hasn't given a number,
   ask for one or infer a reasonable target from context (e.g. "p99 API
   latency under 200ms").
2. **Reproduce it measurably.** Get a benchmark or profile *before*
   touching any code. Without a "before" number, you can't tell if a
   change helped, did nothing, or made it worse.
3. **Profile, don't guess.** Use a profiler to find where time/memory is
   actually spent. The bottleneck is very often not where people assume
   (a "slow" outer loop is often waiting on one cheap-looking I/O call
   inside it, not on the loop's own logic).
4. **Fix the biggest bottleneck first.** Amdahl's law: speeding up code
   that's 2% of total time by 10x saves ~1.8% overall. Find the thing
   that dominates, fix that, re-measure, repeat.
5. **Re-measure after every change.** Confirm the fix actually helped,
   by the same method used for the "before" number. Don't stack multiple
   unverified changes — you won't know which one mattered, or whether one
   of them made things worse while another compensated.
6. **Stop when the target is met.** Further optimization past the actual
   requirement is wasted engineering time and often adds complexity/risk
   for no user-facing benefit.

## 1. Classify the bottleneck type first

Before picking a tool, narrow down what kind of bottleneck you're likely
looking at — it changes which profiler is useful:

| Symptom | Likely category | Start with |
|---|---|---|
| High CPU usage, process pegged at 100% | CPU-bound | CPU profiler (sampling or deterministic) |
| Low CPU usage but still slow | I/O-bound (disk, network, DB) | Tracing/logging around I/O calls, DB query stats |
| Memory grows over time / OOM | Memory leak or unbounded growth | Memory profiler / heap snapshot |
| Fast alone, slow under load | Contention (locks, connection pool, thread starvation) | Concurrency profiler, load test with tracing |
| Slow on first call, fast after | Cold start / cache miss / JIT warmup | Compare cold vs warm timing explicitly |

## 2. Tools by language

### Python
```bash
# Quick wall-clock check of a function, no setup required
python -m timeit -s "from mymodule import myfunc" "myfunc(test_input)"

# CPU profiling — deterministic, good for finding which function dominates
python -m cProfile -s cumulative myscript.py

# Line-by-line CPU profiling (pip install line_profiler)
kernprof -l -v myscript.py     # requires @profile decorator on target function

# Memory profiling (pip install memory_profiler)
python -m memory_profiler myscript.py

# Statistical/sampling profiler with flamegraph output (pip install py-spy)
py-spy record -o profile.svg -- python myscript.py
py-spy dump --pid <pid>        # inspect a running process without restarting it
```

### Node.js
```bash
# Built-in CPU profiler
node --prof app.js
node --prof-process isolate-*.log > processed.txt

# Flamegraph via clinic.js
npx clinic flame -- node app.js

# Heap snapshot for memory leaks
node --inspect app.js   # then take heap snapshots in Chrome DevTools
```

### General / black-box (any language, HTTP services)
```bash
# Load testing + latency percentiles
hey -n 1000 -c 50 https://api.example.com/endpoint
wrk -t4 -c100 -d30s https://api.example.com/endpoint

# Database query timing (Postgres)
EXPLAIN ANALYZE SELECT ...;
```

## 3. Interpreting profiler output

- **Self time vs. cumulative time.** Self time = time in the function
  itself; cumulative = self time + everything it calls. A function with
  high cumulative but low self time isn't the bottleneck — trace into
  what it calls instead.
- **Sampling vs. deterministic profilers.** Deterministic (e.g. `cProfile`)
  instruments every call and has overhead that can distort timing,
  especially for tight loops; sampling (e.g. `py-spy`) periodically
  snapshots the call stack with near-zero overhead, better for production
  or hot-loop profiling. Use sampling when the profiler's own overhead
  might be the story.
- **Flamegraphs read bottom-up.** Width = time spent; a wide bar in the
  middle of the stack is the actual hotspot, not necessarily the topmost
  frame.
- **Watch for profiler artifacts.** The very first call after process
  start is often slower (imports, JIT warmup, cache misses) — don't let
  cold-start cost dominate a benchmark unless cold start is literally
  what's being measured.

## 4. Common root causes, roughly by frequency

1. **N+1 queries** — one query per item in a loop instead of one batched
   query. The single most common "mysteriously slow" pattern in web apps.
2. **Missing database index** on a column used in `WHERE`/`JOIN`/`ORDER BY`.
3. **Synchronous I/O blocking a thread** that could be async/concurrent.
4. **Unbounded data structure growth** (a cache with no eviction, an
   ever-growing list appended to in a long-lived process).
5. **Repeated expensive computation** that could be cached/memoized
   (recomputing the same pure-function result every call).
6. **Serialization overhead** — over-fetching more data than needed and
   paying to parse/serialize it (e.g. `SELECT *` when 2 columns are used).
7. **Algorithmic complexity mismatch** — O(n²) where the data size has
   grown past what a quadratic algorithm tolerates; only worth fixing if
   the profiler actually shows this loop dominating, not by inspection alone.

## 5. Benchmarking correctly (avoiding fake wins)

- Warm up before timing (run once, discard, then time subsequent runs) —
  unless cold start is the thing being measured.
- Run multiple iterations and report a distribution (median, p95), not
  a single run — single-run timings are noisy.
- Benchmark on realistic data size and shape, not a toy input that fits
  entirely in cache and hides the actual bottleneck.
- Control for other load on the machine; a noisy-neighbor process can
  swing results more than the code change being tested.
- When comparing before/after, change one thing at a time and re-run the
  full benchmark, not just eyeball a single number.

## Anti-pattern checklist

- [ ] Optimizing before profiling ("this loop looks slow" without a number)
- [ ] Reporting a single-run timing instead of a distribution
- [ ] Stacking multiple unverified optimizations in one change
- [ ] Micro-optimizing a function that's 1% of total time while the real
      bottleneck (often I/O or a query) goes unmeasured
- [ ] Benchmarking on unrealistically small/cached-friendly test data
- [ ] Declaring victory without re-measuring after the fix
- [ ] Adding caching/complexity to "fix" something that was never
      actually confirmed to be the bottleneck

## Worked example

**Report:** "This endpoint takes 3 seconds, please make it faster."

```
Step 1 — Define target: user wants it under 500ms (p95).

Step 2 — Reproduce with a number:
    hey -n 50 -c 1 https://api.example.com/orders/summary
    → p95: 3.1s   (baseline recorded before any change)

Step 3 — Profile instead of guessing:
    py-spy record -o before.svg -- python app.py
    → flamegraph shows 92% of time inside `get_order_items()`,
      which calls `db.query()` once per order in a loop (100 orders
      → 100 queries) — classic N+1.

Step 4 — Fix the actual bottleneck:
    Replace the per-order query loop with one batched query:
        SELECT * FROM order_items WHERE order_id IN (...)

Step 5 — Re-measure with the same benchmark:
    hey -n 50 -c 1 https://api.example.com/orders/summary
    → p95: 180ms

Step 6 — Target met (500ms goal, achieved 180ms) — stop here rather
than further micro-optimizing a now-fast path.
```

Note what did NOT happen: no rewriting of unrelated "slow-looking" code,
no caching layer bolted on speculatively, no algorithm swap — because the
profiler identified one specific, dominant cause, and fixing that one
thing hit the target.

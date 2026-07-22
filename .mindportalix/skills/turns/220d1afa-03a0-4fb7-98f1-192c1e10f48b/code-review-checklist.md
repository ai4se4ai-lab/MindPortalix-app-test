---
name: code-review-checklist
description: >
  Use this skill whenever reviewing a pull request, diff, or code change —
  whether asked to "review this PR", "check this diff", "what's wrong with
  this code", "is this ready to merge", or when the user pastes a code change
  and asks for feedback before merging/shipping it. Also apply proactively
  when asked to review someone else's code changes, not just author code.
  Covers cross-cutting review concerns (correctness, security, tests,
  readability, API/breaking-change impact) rather than language-specific
  style — pair with the relevant clean-code-<language> skill for style-level
  nits. Do NOT use this for reviewing a whole unfamiliar codebase from
  scratch (that's an audit/onboarding task, not a PR review), and do NOT use
  it purely to write new code — use it only when the artifact under
  discussion is a proposed *change* to existing code.
location: /skills/code-review-checklist.md
---

# Code Review Checklist

A good review finds the few things that actually matter and says nothing
about the rest. Work through the categories below in order — correctness
and safety first, style last — and stop elaborating once a category is clean.

## 0. Before reviewing line-by-line

- Understand *what* the change is trying to do and *why*, from the PR
  description/commit message/linked issue — not just the diff. If intent
  is unclear, that's the first comment, not a guess at intent.
- Check the size of the change. A 800-line diff touching 12 unrelated
  things should get one comment — "please split this" — before a
  line-by-line review, not after.
- Note what's NOT in the diff that should be: missing tests, missing docs,
  missing migration, missing changelog entry.

## 1. Correctness (highest priority)

- Does the code actually do what the PR claims? Trace the logic against
  the stated intent, not just against "does it look reasonable."
- Check edge cases explicitly: empty input, null/None, zero, negative
  numbers, very large input, duplicate entries, concurrent access.
- Off-by-one errors in loops, slices, and boundary conditions.
- Check error paths, not just the happy path — what happens when a
  dependency call fails, times out, or returns unexpected data?
- For anything involving state mutation: is there a race condition or
  an ordering assumption that isn't guaranteed?

## 2. Security

- Is user input validated/sanitized before use (queries, shell commands,
  file paths, template rendering)?
- Are secrets, tokens, or credentials hardcoded or logged anywhere?
- Are new external inputs (API params, file uploads, webhooks) treated
  as untrusted?
- Does this change auth/permission logic? If so, verify the *new*
  permission boundary explicitly rather than assuming it's equivalent
  to the old one.
- New dependency added? Briefly sanity-check it's a maintained,
  reasonably trusted package, not a redundant addition.

## 3. Tests

- Are there tests for the new behavior, not just for the happy path?
- Do the tests actually assert something meaningful, or just that "no
  exception was thrown"?
- Were any existing tests weakened, skipped, or deleted to make this
  change pass? That's a red flag requiring justification, not a
  silent pass.
- For a bug fix: is there a regression test that would have caught the
  original bug?

## 4. API & breaking-change impact

- Does this change a public function signature, endpoint contract, or
  database schema in a way that breaks existing callers?
- If it's a breaking change, is it versioned/flagged/documented as one,
  or does it silently change behavior for existing consumers?
- Backward compatibility: can this be rolled back safely if it ships
  and causes a problem?
- For schema changes: is the migration safe to run on a live system
  (no long-locking operations on large tables, no dropped column before
  code stops reading it)?

## 5. Readability & maintainability

- Can a reviewer understand *why* a non-obvious decision was made, or
  does it need a comment that isn't there?
- Is the change consistent with existing patterns in the codebase, or
  does it introduce a new pattern without justification (new pattern ≠
  automatically wrong, but it should be a deliberate, flagged choice)?
- Naming: do new functions/variables communicate intent (see
  clean-code-<language> skill for detailed naming rules)?
- Is there duplicated logic that already exists elsewhere in the
  codebase and could be reused instead?

## 6. Performance (only where it plausibly matters)

- Any obviously expensive operation inside a loop that runs per-request
  or per-item at scale (N+1 queries, repeated I/O, unbounded recursion)?
- New data structure/algorithm choice appropriate for the expected data
  size — don't demand micro-optimization for code that runs once at
  startup on tiny input.

## 7. Scope discipline

- Does the diff do only what the PR claims, or does it sneak in
  unrelated refactors, formatting-only changes, or drive-by fixes that
  make the diff harder to review and revert? Flag scope creep even if
  the unrelated change is itself fine — it belongs in its own PR.

## How to phrase feedback

- Separate **blocking** issues from **nice-to-have** suggestions
  explicitly — don't make an author guess which comments gate the merge.
  Prefix style: `[blocking]` vs `[nit]` / `[question]` / `[suggestion]`.
- Ask, don't assert, when you're inferring intent: "Is this intentionally
  skipping the null case, or should it be handled?" rather than assuming
  malice or carelessness.
- Point at the *pattern*, not just the instance, when a fix generalizes:
  "this same missing-null-check pattern shows up in `parse_input` too."
- Praise good decisions briefly when you see them — a review that's 100%
  negative reads as adversarial even when every point is valid.

## Anti-pattern checklist (what a WEAK review looks like — avoid these)

- [ ] Only commenting on formatting/style while missing a logic bug
- [ ] Approving because "tests pass" without reading the tests
      themselves for whether they assert anything meaningful
- [ ] Reviewing the diff without reading the surrounding unchanged code
      needed to know if the change is correct in context
- [ ] Vague comments ("this could be better") with no concrete suggestion
- [ ] Nitpicking a huge diff line-by-line instead of first asking for it
      to be split
- [ ] Rubber-stamping because the PR is from a senior/trusted author
- [ ] Missing that a test was deleted/weakened to make the change pass

## Worked example

**Diff under review:**
```python
def get_user_discount(user_id):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    if user.tier == "gold":
        return 0.2
    return 0.1
```

**Review output:**

```
[blocking] SQL injection: user_id is interpolated directly into the query
string. Use a parameterized query:
    db.query("SELECT * FROM users WHERE id = %s", (user_id,))

[blocking] No handling for user_id not found — db.query(...) result is
used as `user.tier` with no check that `user` exists. What happens on a
deleted/invalid id?

[question] Is 0.1 the discount for every non-gold tier, or should silver/
bronze be distinguished? Worth a comment either way so the next reader
doesn't have to guess.

[nit] Function could use a type hint on the return value (`-> float`) and
on `user_id` (`-> int`), consistent with the rest of this module.

[missing] No test coverage for this function — at minimum, cases for
gold user, non-gold user, and unknown user_id would catch the missing-user
bug above.
```

This example shows the priority order in practice: the security bug and
the missing-user bug are `[blocking]` and come first; a genuine ambiguity
becomes a `[question]`, not an assumption; style is a `[nit]` at the end;
and the missing test coverage is called out explicitly rather than silently
noted only as "LGTM once tests are added."

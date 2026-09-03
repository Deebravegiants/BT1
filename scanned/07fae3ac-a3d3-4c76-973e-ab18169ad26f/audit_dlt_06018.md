# [?] fix(iroh): bind failure returns error instead of panicking (#8518)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-04-16
Source: https://github.com/fedimint/fedimint/commit/de0edd6487e18cd0f26676058f7af97707ee1d18
Type: security-commit

## Details
fix(iroh): bind failure returns error instead of panicking (#8518)

Change `build_iroh_endpoint` to propagate bind errors with `?` instead
of using `.expect()`, allowing callers to handle failures gracefully.

Re: #8482

<!--

# Code Review Policy

* CI must pass (enforced)
* 1 review is mandatory (enforced), 2 or more ideal
* If you believe your change is simple, and non-controversial enough,
and you want
to avoid merge conflicts, or blocking work before it gets enough
reviews, label it with
  `needs further review` label and Merge it.

See
https://github.com/fedimint/fedimint/blob/master/CONTRIBUTING.md#code-review-policy
for
full description.

-->

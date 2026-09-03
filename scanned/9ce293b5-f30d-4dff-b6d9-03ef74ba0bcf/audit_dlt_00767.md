# [?] fix(pbts): hardening tests for overflows in `SynchronyParams` (#4816)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2025-01-30
Source: https://github.com/cometbft/cometbft/commit/972fa8038b57cc2152cb67144869ccd604526550
Type: security-commit

## Details
fix(pbts): hardening tests for overflows in `SynchronyParams` (#4816)

Closes #4815.

The added test units allowed us to catch overflow scenarios in some
architectures, in particular `linux/amd64`. The same is not observed in
the `arm64` architecture. Sanity checks were added to prevent this from
happening.

Further more, `MessageDelay` is now capped at 24hrs, `Precision` - 30
sec.

---------

Co-authored-by: Anton Kaliaev <anton.kalyaev@gmail.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

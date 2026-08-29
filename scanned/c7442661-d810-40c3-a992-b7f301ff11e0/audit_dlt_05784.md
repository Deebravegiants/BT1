# [?] fix(lanes): Panic when lane is not found (#4169)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-09-24
Source: https://github.com/cometbft/cometbft/commit/3329e68931bccdf2e338c8c002f3845a16a4bf8b
Type: security-commit

## Details
fix(lanes): Panic when lane is not found (#4169)

There is always at least one lane, so it should not happen that a lane
is not found. This has cost me some debugging time.

---------

Co-authored-by: Jasmina Malicevic <jasmina.dustinac@gmail.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

# Q3338: write-feeds via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the full batch list and its ordering, can an unprivileged attacker make `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) leave a residue that no reconciliation pass ever inspects? `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the full batch list and its ordering varied, and assert that the value `write-feeds` returns is identical in both runs; a divergence confirms the finding.

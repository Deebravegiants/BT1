# Q3690: check-confidence via call-ststx-ratio: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling the block and transaction position at which the external ratio is fetched, can an unprivileged attacker make `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) leave a residue that no reconciliation pass ever inspects? `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `call-ststx-ratio` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the block and transaction position at which the external ratio is fetched across its boundary values through `call-ststx-ratio` in simnet and assert `check-confidence` never returns a value that breaks the invariant.

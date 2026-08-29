# Q3206: resolve-pyth via call-ststx-ratio: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling the block and transaction position at which the external ratio is fetched, can an unprivileged attacker make `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) leave a residue that no reconciliation pass ever inspects? `resolve-pyth` reads the Pyth storage record for a 32-byte ident, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `call-ststx-ratio` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `resolve-pyth` returns is identical in both runs; a divergence confirms the finding.

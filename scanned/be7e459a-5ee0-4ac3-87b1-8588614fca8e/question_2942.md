# Q2942: calc-multiplier-delta via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the position state the final collateral-add is validated against, can an unprivileged attacker make `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) leave a residue that no reconciliation pass ever inspects? `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with the position state the final collateral-add is validated against varied, and assert that the value `calc-multiplier-delta` returns is identical in both runs; a divergence confirms the finding.

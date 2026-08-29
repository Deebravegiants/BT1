# Q0062: insert via collateral-add: mint shares whose backing was never received

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling `amount`, can an unprivileged attacker make `insert` (mainnet/contracts/market/v0-market-vault.clar:159) mint shares whose backing was never received? `insert` rewrites the whole registry entry for a user id, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `insert` returns is identical in both runs; a divergence confirms the finding.

# Q0410: get-bitmap via collateral-remove: mint shares whose backing was never received

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) mint shares whose backing was never received? `get-bitmap` returns the global enabled bitmap that every position read filters on, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `receiver`, including a contract principal varied, and assert that the value `get-bitmap` returns is identical in both runs; a divergence confirms the finding.

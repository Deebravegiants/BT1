# Q0482: receive-tokens via supply-collateral-add: mint shares whose backing was never received

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) mint shares whose backing was never received? `receive-tokens` pulls an asset from a named account, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `min-shares` (the only slippage bound on the deposit leg) varied, and assert that the value `receive-tokens` returns is identical in both runs; a divergence confirms the finding.

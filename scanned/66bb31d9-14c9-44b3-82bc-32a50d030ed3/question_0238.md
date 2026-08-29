# Q0238: receive-tokens via collateral-remove: mint shares whose backing was never received

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling whether the position has any enabled debt row (the has-debt branch), can an unprivileged attacker make `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) mint shares whose backing was never received? `receive-tokens` pulls an asset from a named account, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove` with whether the position has any enabled debt row (the has-debt branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.

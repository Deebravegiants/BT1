# Q5341: next-liquidity-index via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling call ordering within the block, drive `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) — which rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with call ordering within the block, then read `next-liquidity-index` state before and after in the same block and assert the two sides of the invariant are equal.

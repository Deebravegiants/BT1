# Q4756: resolve-ztoken via liquidate-multi: mint shares whose backing was never received

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `resolve-ztoken` (mainnet/contracts/market/v0-4-market.clar:343) in a state where it mint shares whose backing was never received? Given that it reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:343` -> `resolve-ztoken`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-multi` with the trait principals supplied per entry, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.

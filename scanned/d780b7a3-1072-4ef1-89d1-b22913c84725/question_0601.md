# Q0601: resolve-ztoken via borrow: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `resolve-ztoken` (mainnet/contracts/market/v0-4-market.clar:343) — which reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:343` -> `resolve-ztoken`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with `amount`, then read `resolve-ztoken` state before and after in the same block and assert the two sides of the invariant are equal.

# Q0901: iter-price-multi via borrow: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `iter-price-multi` (mainnet/contracts/market/v0-4-market.clar:405) — which carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64` — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:405` -> `iter-price-multi`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `iter-price-multi` carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with `amount`, then read `iter-price-multi` state before and after in the same block and assert the two sides of the invariant are equal.

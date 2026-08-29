# Q3173: unpack-u16 via borrow: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `receiver`, including a contract principal, drive `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) — which unpacks eight u16 curve fields from one packed word — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `receiver`, including a contract principal, and assert the attacker's net token balance change is zero or negative.

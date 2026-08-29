# Q5628: socialize-debt via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the future mask produced by the new debt bit reach `socialize-debt` (mainnet/contracts/vault/v0-vault-stx.clar:944) in a state where it record a repayment larger than the value actually delivered? Given that it writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:944` -> `socialize-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `socialize-debt` writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the future mask produced by the new debt bit across its boundary values through `borrow` in simnet and assert `socialize-debt` never returns a value that breaks the invariant.

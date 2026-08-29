# Q4920: get-available-assets via redeem: record a repayment larger than the value actually delivere

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) in a state where it record a repayment larger than the value actually delivered? Given that it reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the gap between the `assets` var and the real balance across its boundary values through `redeem` in simnet and assert `get-available-assets` never returns a value that breaks the invariant.

# Q1206: get-available-assets via accrue: record a repayment larger than the value actually delivere

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) record a repayment larger than the value actually delivered? `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the block time at which accrual is first triggered in a block across its boundary values through `accrue` in simnet and assert `get-available-assets` never returns a value that breaks the invariant.

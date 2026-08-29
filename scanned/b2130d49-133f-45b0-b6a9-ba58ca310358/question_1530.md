# Q1530: ubalance via accrue: record a repayment larger than the value actually delivere

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) record a repayment larger than the value actually delivered? `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the block time at which accrual is first triggered in a block across its boundary values through `accrue` in simnet and assert `ubalance` never returns a value that breaks the invariant.

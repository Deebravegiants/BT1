# Q1002: convert-to-shares-preview via accrue: record a repayment larger than the value actually delivere

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) record a repayment larger than the value actually delivered? `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the block time at which accrual is first triggered in a block across its boundary values through `accrue` in simnet and assert `convert-to-shares-preview` never returns a value that breaks the invariant.

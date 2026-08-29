# Q1938: accrue-user-collateral via accrue: record a repayment larger than the value actually delivere

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) record a repayment larger than the value actually delivered? `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the block time at which accrual is first triggered in a block across its boundary values through `accrue` in simnet and assert `accrue-user-collateral` never returns a value that breaks the invariant.

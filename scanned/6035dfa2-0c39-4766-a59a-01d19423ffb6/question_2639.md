# Q2639: interpolate-rate via accrue: destroy value through a truncation the opposite operation 

## Question
`interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) interpolates between packed u16 curve points. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the block time at which accrual is first triggered in a block, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `accrue` call, then the attacker-shaped one with the block time at which accrual is first triggered in a block, and assert the attacker's net token balance change is zero or negative.

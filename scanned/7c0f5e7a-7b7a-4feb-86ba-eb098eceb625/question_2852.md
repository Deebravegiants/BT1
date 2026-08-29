# Q2852: next-liquidity-index via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the block time at which accrual is first triggered in a block reach `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) in a state where it credit one side of an accounting pair without the other? Given that it rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the block time at which accrual is first triggered in a block varied, and assert that the value `next-liquidity-index` returns is identical in both runs; a divergence confirms the finding.

# Q2816: next-liquidity-index via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `recipient` reach `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) in a state where it credit one side of an accounting pair without the other? Given that it rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `recipient` varied, and assert that the value `next-liquidity-index` returns is identical in both runs; a divergence confirms the finding.

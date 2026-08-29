# Q4139: send-underlying via redeem: credit one side of an accounting pair without the other

## Question
`send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) pushes the underlying under an `as-contract?` post-condition scope. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `recipient`, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `redeem` call, then the attacker-shaped one with `recipient`, and assert the attacker's net token balance change is zero or negative.

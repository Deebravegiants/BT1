# Q2504: debt-preview via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `amount` of shares burned reach `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) in a state where it credit one side of an accounting pair without the other? Given that it computes cumulative debt from `principal-scaled` and the FORWARD index, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `amount` of shares burned varied, and assert that the value `debt-preview` returns is identical in both runs; a divergence confirms the finding.

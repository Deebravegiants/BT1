# Q0710: vault-accrue via deposit: mint shares whose backing was never received

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling whether the vault is at a zero-supply or zero-asset edge, can an unprivileged attacker make `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) mint shares whose backing was never received? `vault-accrue` dispatches accrual to one of six vaults by asset id, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with whether the vault is at a zero-supply or zero-asset edge varied, and assert that the value `vault-accrue` returns is identical in both runs; a divergence confirms the finding.

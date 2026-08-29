# Q0506: accrue-user-collateral via deposit: mint shares whose backing was never received

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `amount`, can an unprivileged attacker make `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) mint shares whose backing was never received? `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `amount` varied, and assert that the value `accrue-user-collateral` returns is identical in both runs; a divergence confirms the finding.

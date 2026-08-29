# Q3596: calc-utilization via deposit: make the per-user ledger and the vault aggregate disagree 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls the vault's supply and asset state at the moment of the call reach `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it divides debt by available liquidity, which can exceed BPS when debt outruns assets, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `deposit` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with the vault's supply and asset state at the moment of the call varied, and assert that the value `calc-utilization` returns is identical in both runs; a divergence confirms the finding.

# Q1202: send-underlying via redeem: record a repayment larger than the value actually delivere

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `recipient`, can an unprivileged attacker make `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) record a repayment larger than the value actually delivered? `send-underlying` pushes the underlying under an `as-contract?` post-condition scope, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `recipient` varied, and assert that the value `send-underlying` returns is identical in both runs; a divergence confirms the finding.

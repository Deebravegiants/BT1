# Q1514: get-available-assets via deposit: record a repayment larger than the value actually delivere

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling whether the vault is at a zero-supply or zero-asset edge, can an unprivileged attacker make `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) record a repayment larger than the value actually delivered? `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `deposit` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with whether the vault is at a zero-supply or zero-asset edge varied, and assert that the value `get-available-assets` returns is identical in both runs; a divergence confirms the finding.

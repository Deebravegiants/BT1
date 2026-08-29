# Q1758: resolve-interpolation-points via deposit: record a repayment larger than the value actually delivere

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling the vault's supply and asset state at the moment of the call, can an unprivileged attacker make `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) record a repayment larger than the value actually delivered? `resolve-interpolation-points` selects the bracketing curve points for a utilization, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `deposit` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the vault's supply and asset state at the moment of the call across its boundary values through `deposit` in simnet and assert `resolve-interpolation-points` never returns a value that breaks the invariant.

# Q1278: accrue via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling the zToken/underlying id mapping reached (the u100 sentinel branch), can an unprivileged attacker make `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) record a repayment larger than the value actually delivered? `accrue` advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:835` -> `accrue`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `accrue` advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the zToken/underlying id mapping reached (the u100 sentinel branch) across its boundary values through `collateral-remove-redeem` in simnet and assert `accrue` never returns a value that breaks the invariant.

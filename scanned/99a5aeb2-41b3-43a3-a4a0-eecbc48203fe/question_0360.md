# Q0360: next-index via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls remaining zToken collateral whose price moves with the redeem reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz remaining zToken collateral whose price moves with the redeem across its boundary values through `collateral-remove-redeem` in simnet and assert `next-index` never returns a value that breaks the invariant.

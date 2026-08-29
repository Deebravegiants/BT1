# Q0060: next-index via redeem: destroy value through a truncation the opposite operation 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the gap between the `assets` var and the real balance across its boundary values through `redeem` in simnet and assert `next-index` never returns a value that breaks the invariant.

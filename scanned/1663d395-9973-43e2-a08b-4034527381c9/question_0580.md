# Q0580: calc-cumulative-debt via deposit: destroy value through a truncation the opposite operation 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it multiplies scaled principal by an index, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `deposit` with whether the vault is at a zero-supply or zero-asset edge, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.

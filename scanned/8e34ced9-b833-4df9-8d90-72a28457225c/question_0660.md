# Q0660: add-user-collateral via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it adds to the collateral row with a graceful u0 default, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the set of assets held across its boundary values through `collateral-remove` in simnet and assert `add-user-collateral` never returns a value that breaks the invariant.

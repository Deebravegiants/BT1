# Q0732: zip via collateral-add: destroy value through a truncation the opposite operation 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it pairs the utilization and rate point lists element by element, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz call ordering within the block across its boundary values through `collateral-add` in simnet and assert `zip` never returns a value that breaks the invariant.

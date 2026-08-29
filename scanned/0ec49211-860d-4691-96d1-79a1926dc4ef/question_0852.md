# Q0852: send-tokens via collateral-add: destroy value through a truncation the opposite operation 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it pushes an asset to a caller-chosen recipient principal, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz call ordering within the block across its boundary values through `collateral-add` in simnet and assert `send-tokens` never returns a value that breaks the invariant.

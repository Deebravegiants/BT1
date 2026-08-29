# Q5961: resolve-or-create via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the vault whose share price the redemption moves, drive `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) — which allocates a user id through `increment` for whatever principal the market names — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-or-create` touches, run `liquidate-redeem` with the vault whose share price the redemption moves, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

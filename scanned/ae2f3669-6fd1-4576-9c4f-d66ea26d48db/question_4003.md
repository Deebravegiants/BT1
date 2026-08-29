# Q4003: resolve-or-create via liquidate-redeem: credit one side of an accounting pair without the other

## Question
`resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) allocates a user id through `increment` for whatever principal the market names. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the vault whose share price the redemption moves, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the vault whose share price the redemption moves, then read `resolve-or-create` state before and after in the same block and assert the two sides of the invariant are equal.

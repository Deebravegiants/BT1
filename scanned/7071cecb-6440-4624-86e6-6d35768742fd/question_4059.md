# Q4059: increment via liquidate-redeem: credit one side of an accounting pair without the other

## Question
`increment` (mainnet/contracts/market/v0-market-vault.clar:137) advances the user-id nonce. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the vault whose share price the redemption moves, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `increment` advances the user-id nonce. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `increment` touches, run `liquidate-redeem` with the vault whose share price the redemption moves, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

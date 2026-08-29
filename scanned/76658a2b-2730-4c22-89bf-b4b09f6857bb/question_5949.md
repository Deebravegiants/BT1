# Q5949: increment via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the `ft` trait principal, drive `increment` (mainnet/contracts/market/v0-market-vault.clar:137) — which advances the user-id nonce — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `increment` advances the user-id nonce. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `increment` touches, run `collateral-remove` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

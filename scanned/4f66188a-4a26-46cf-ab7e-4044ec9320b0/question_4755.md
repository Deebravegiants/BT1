# Q4755: collateral-add via collateral-add: credit one side of an accounting pair without the other

## Question
`collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the `ft` trait principal, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `collateral-add` touches, run `collateral-add` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

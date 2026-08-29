# Q4731: collateral-remove via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
`collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) decrements the map and writes the entry before `send-tokens` executes. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing remaining zToken collateral whose price moves with the redeem, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `collateral-remove` touches, run `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

# Q0717: write-feed via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `min-underlying`, drive `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) — which applies one Pyth price-feed update and folds its status — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `write-feed` touches, run `collateral-remove-redeem` with `min-underlying`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

# Q0261: get-asset-value via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `amount`, drive `get-asset-value` (mainnet/contracts/market/v0-4-market.clar:679) — which resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:679` -> `get-asset-value`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-asset-value` touches, run `supply-collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

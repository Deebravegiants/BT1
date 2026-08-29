# Q0513: send-tokens via liquidate: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `min-collateral-expected`, drive `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) — which pushes an asset to a caller-chosen recipient principal — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `send-tokens` touches, run `liquidate` with `min-collateral-expected`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

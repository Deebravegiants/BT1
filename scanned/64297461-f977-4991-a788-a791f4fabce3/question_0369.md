# Q0369: get-account-scaled-debt via liquidate: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `min-collateral-expected`, drive `get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) — which reads one scaled debt row — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `get-account-scaled-debt` touches, run `liquidate` with `min-collateral-expected`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

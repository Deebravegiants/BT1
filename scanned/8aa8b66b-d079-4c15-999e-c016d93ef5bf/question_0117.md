# Q0117: iter-lookup-collateral via borrow: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the `ft` trait principal, drive `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) — which skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `iter-lookup-collateral` touches, run `borrow` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

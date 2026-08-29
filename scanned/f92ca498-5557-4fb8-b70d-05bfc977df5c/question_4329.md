# Q4329: remove-user-scaled-debt via borrow: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `remove-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:244) — which deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:244` -> `remove-user-scaled-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `remove-user-scaled-debt` deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `remove-user-scaled-debt` touches, run `borrow` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

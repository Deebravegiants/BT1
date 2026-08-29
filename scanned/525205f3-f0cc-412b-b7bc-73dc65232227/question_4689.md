# Q4689: create via borrow: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `create` (mainnet/contracts/market/v0-market-vault.clar:150) — which binds a principal to a fresh numeric id — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `create` touches, run `borrow` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

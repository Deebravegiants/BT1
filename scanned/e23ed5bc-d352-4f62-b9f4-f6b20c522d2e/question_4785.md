# Q4785: add-user-collateral via borrow: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) — which adds to the collateral row with a graceful u0 default — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `add-user-collateral` touches, run `borrow` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

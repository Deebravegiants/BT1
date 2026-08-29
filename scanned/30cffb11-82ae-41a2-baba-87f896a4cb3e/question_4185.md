# Q4185: resolve-pyth via call-ststx-ratio: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling the block and transaction position at which the external ratio is fetched, drive `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) — which reads the Pyth storage record for a 32-byte ident — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `call-ststx-ratio` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-pyth` touches, run `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

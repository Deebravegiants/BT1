# Q4737: resolve-pyth via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `amount`, drive `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) — which reads the Pyth storage record for a 32-byte ident — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-pyth` touches, run `supply-collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

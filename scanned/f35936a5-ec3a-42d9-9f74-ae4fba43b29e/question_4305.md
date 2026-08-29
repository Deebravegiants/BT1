# Q4305: add-user-collateral via transfer: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the destination principal, including the market, the market-vault or the treasury, drive `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) — which adds to the collateral row with a graceful u0 default — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `add-user-collateral` touches, run `transfer` with the destination principal, including the market, the market-vault or the treasury, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

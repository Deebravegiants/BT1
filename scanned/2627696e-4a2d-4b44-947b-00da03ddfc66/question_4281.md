# Q4281: total-assets via transfer: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the destination principal, including the market, the market-vault or the treasury, drive `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) — which adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `total-assets` touches, run `transfer` with the destination principal, including the market, the market-vault or the treasury, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

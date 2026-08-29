# Q4425: accrue-user-debts via redeem: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling the vault's available liquidity relative to the redemption, drive `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) — which folds accrual over the position's debt list only — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `accrue-user-debts` touches, run `redeem` with the vault's available liquidity relative to the redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

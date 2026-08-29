# Q3903: accrue-user-debts via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
`accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) folds accrual over the position's debt list only. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the redemption receiver, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `accrue-user-debts` touches, run `liquidate-redeem` with the redemption receiver, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

# Q3660: find-asset via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the vault whose share price the redemption moves reach `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the vault whose share price the redemption moves across its boundary values through `liquidate-redeem` in simnet and assert `find-asset` never returns a value that breaks the invariant.

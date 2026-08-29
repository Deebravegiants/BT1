# Q0807: check-confidence via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
`check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the vault whose share price the redemption moves, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `check-confidence` touches, run `liquidate-redeem` with the vault whose share price the redemption moves, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

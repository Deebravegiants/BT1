# Q3708: write-feeds via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `write-feeds` never returns a value that breaks the invariant.

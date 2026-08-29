# Q3888: get-notional-evaluation via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the three `price-feeds` buffers and their order reach `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the three `price-feeds` buffers and their order across its boundary values through `collateral-add` in simnet and assert `get-notional-evaluation` never returns a value that breaks the invariant.

# Q3624: convert-to-scaled-debt via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it scales a token amount by the cached borrow index, rounding up on the borrow path, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-underlying` across its boundary values through `collateral-remove-redeem` in simnet and assert `convert-to-scaled-debt` never returns a value that breaks the invariant.

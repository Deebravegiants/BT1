# Q3816: mask-to-list-collateral via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls the `ft` trait principal reach `mask-to-list-collateral` (mainnet/contracts/market/v0-4-market.clar:449) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it expands a mask to a list of ids over ITER-UINT-64, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:449` -> `mask-to-list-collateral`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `mask-to-list-collateral` expands a mask to a list of ids over ITER-UINT-64. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `repay` in simnet and assert `mask-to-list-collateral` never returns a value that breaks the invariant.

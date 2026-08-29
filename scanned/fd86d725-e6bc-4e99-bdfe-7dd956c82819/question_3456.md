# Q3456: iter-find-superset via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it short-circuits on the first superset match, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `borrow` in simnet and assert `iter-find-superset` never returns a value that breaks the invariant.

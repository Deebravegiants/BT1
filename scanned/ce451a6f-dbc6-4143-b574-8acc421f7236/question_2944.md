# Q2944: active via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `active` (mainnet/contracts/registry/v0-egroup.clar:238) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it lists candidate bucket masks at or above a population, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.

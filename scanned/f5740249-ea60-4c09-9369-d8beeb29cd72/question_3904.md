# Q3904: get-full-position via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `borrower`, any third-party principal reach `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it returns all collateral rows regardless of the enabled bitmap, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with `borrower`, any third-party principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.

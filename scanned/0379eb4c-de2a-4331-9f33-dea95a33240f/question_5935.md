# Q5935: insert via liquidate: mint shares whose backing was never received

## Question
`insert` (mainnet/contracts/market/v0-market-vault.clar:159) rewrites the whole registry entry for a user id. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `borrower`, any third-party principal, use that to mint shares whose backing was never received, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `borrower`, any third-party principal, then read `insert` state before and after in the same block and assert the two sides of the invariant are equal.

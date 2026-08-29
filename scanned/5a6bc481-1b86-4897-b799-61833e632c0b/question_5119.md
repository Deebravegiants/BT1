# Q5119: relevant via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
`relevant` (mainnet/contracts/market/v0-market-vault.clar:175) drops any position row whose bit is not present in the enabled mask. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing call ordering within the block, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with call ordering within the block, then read `relevant` state before and after in the same block and assert the two sides of the invariant are equal.

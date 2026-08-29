# Q4047: relevant via repay: credit one side of an accounting pair without the other

## Question
`relevant` (mainnet/contracts/market/v0-market-vault.clar:175) drops any position row whose bit is not present in the enabled mask. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing the `ft` trait principal, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `relevant` touches, run `repay` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

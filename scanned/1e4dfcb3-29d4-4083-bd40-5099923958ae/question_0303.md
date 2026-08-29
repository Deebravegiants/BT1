# Q0303: add-user-scaled-debt via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
`add-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:237) adds to the scaled debt row with a graceful u0 default. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing which borrowers are placed early versus late in the batch, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:237` -> `add-user-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `add-user-scaled-debt` touches, run `liquidate-multi` with which borrowers are placed early versus late in the batch, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

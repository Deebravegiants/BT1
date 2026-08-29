# Q5973: vault-accrue via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) — which dispatches accrual to one of six vaults by asset id — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `vault-accrue` touches, run `liquidate-multi` with which borrowers are placed early versus late in the batch, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

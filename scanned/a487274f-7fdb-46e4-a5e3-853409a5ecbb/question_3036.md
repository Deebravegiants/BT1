# Q3036: vault-accrue via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls which borrowers are placed early versus late in the batch reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it dispatches accrual to one of six vaults by asset id, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz which borrowers are placed early versus late in the batch across its boundary values through `liquidate-multi` in simnet and assert `vault-accrue` never returns a value that breaks the invariant.

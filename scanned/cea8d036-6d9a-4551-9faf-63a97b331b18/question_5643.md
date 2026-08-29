# Q5643: vault-accrue via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
`vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) dispatches accrual to one of six vaults by asset id. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `debt-amount`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `vault-accrue` touches, run `liquidate` with `debt-amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

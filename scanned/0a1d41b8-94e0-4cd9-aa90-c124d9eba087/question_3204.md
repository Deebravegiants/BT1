# Q3204: system-borrow via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls which borrowers are placed early versus late in the batch reach `system-borrow` (mainnet/contracts/vault/v0-vault-stx.clar:865) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:865` -> `system-borrow`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `system-borrow` independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz which borrowers are placed early versus late in the batch across its boundary values through `liquidate-multi` in simnet and assert `system-borrow` never returns a value that breaks the invariant.

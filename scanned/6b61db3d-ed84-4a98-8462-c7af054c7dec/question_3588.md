# Q3588: resolve-pyth via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls which borrowers are placed early versus late in the batch reach `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads the Pyth storage record for a 32-byte ident, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz which borrowers are placed early versus late in the batch across its boundary values through `liquidate-multi` in simnet and assert `resolve-pyth` never returns a value that breaks the invariant.

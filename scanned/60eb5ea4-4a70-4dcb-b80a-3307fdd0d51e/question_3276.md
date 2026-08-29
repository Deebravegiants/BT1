# Q3276: get-egroup via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz vault share price at the moment of the deposit leg across its boundary values through `supply-collateral-add` in simnet and assert `get-egroup` never returns a value that breaks the invariant.

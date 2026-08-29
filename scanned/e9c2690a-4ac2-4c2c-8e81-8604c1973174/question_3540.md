# Q3540: total-supply-preview via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `receiver` for the underlying leg reach `total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `receiver` for the underlying leg across its boundary values through `collateral-remove-redeem` in simnet and assert `total-supply-preview` never returns a value that breaks the invariant.

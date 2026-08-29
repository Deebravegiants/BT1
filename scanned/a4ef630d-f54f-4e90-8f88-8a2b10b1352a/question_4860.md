# Q4860: get-position via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `get-position` (mainnet/contracts/market/v0-4-market.clar:466) in a state where it mint shares whose backing was never received? Given that it returns only rows whose bit is set in the ENABLED bitmap, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz vault share price at the moment of the deposit leg across its boundary values through `supply-collateral-add` in simnet and assert `get-position` never returns a value that breaks the invariant.

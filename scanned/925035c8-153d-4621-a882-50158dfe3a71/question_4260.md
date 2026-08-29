# Q4260: send-underlying via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it mint shares whose backing was never received? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz vault share price at the moment of the deposit leg across its boundary values through `supply-collateral-add` in simnet and assert `send-underlying` never returns a value that breaks the invariant.

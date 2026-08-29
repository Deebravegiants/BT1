# Q4788: resolve-interpolation-points via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) in a state where it mint shares whose backing was never received? Given that it selects the bracketing curve points for a utilization, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `resolve-interpolation-points` never returns a value that breaks the invariant.

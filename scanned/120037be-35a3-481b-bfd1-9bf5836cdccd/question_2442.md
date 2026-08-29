# Q2442: resolve-interpolation-points via repay: have the same quantity scaled twice by two contracts that 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling whether the repaid asset is in the accrued debt list, can an unprivileged attacker make `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) have the same quantity scaled twice by two contracts that round differently? `resolve-interpolation-points` selects the bracketing curve points for a utilization, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the repaid asset is in the accrued debt list across its boundary values through `repay` in simnet and assert `resolve-interpolation-points` never returns a value that breaks the invariant.

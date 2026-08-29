# Q2282: find-superset via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the position's existing collateral and debt composition, can an unprivileged attacker make `find-superset` (mainnet/contracts/registry/v0-egroup.clar:262) have the same quantity scaled twice by two contracts that round differently? `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:262` -> `find-superset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the position's existing collateral and debt composition varied, and assert that the value `find-superset` returns is identical in both runs; a divergence confirms the finding.

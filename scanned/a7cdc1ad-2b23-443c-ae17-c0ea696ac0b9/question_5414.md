# Q5414: iter-find-superset via borrow: count one deposit as backing for two simultaneous claims

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) count one deposit as backing for two simultaneous claims? `iter-find-superset` short-circuits on the first superset match, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `amount` varied, and assert that the value `iter-find-superset` returns is identical in both runs; a divergence confirms the finding.

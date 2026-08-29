# Q5486: active via liquidate: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `borrower`, any third-party principal, can an unprivileged attacker make `active` (mainnet/contracts/registry/v0-egroup.clar:238) count one deposit as backing for two simultaneous claims? `active` lists candidate bucket masks at or above a population, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `borrower`, any third-party principal varied, and assert that the value `active` returns is identical in both runs; a divergence confirms the finding.

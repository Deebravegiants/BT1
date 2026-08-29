# Q5678: status via liquidate: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `borrower`, any third-party principal, can an unprivileged attacker make `status` (mainnet/contracts/registry/v0-assets.clar:115) count one deposit as backing for two simultaneous claims? `status` derives `collateral` and `debt` flags from bit tests against whatever mask it was handed, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:115` -> `status`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `status` derives `collateral` and `debt` flags from bit tests against whatever mask it was handed. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `borrower`, any third-party principal varied, and assert that the value `status` returns is identical in both runs; a divergence confirms the finding.

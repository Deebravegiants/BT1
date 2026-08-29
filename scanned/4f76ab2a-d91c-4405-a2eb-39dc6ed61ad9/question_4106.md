# Q4106: status via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the order of accrual versus price resolution inside the let, can an unprivileged attacker make `status` (mainnet/contracts/registry/v0-assets.clar:115) destroy value through a truncation the opposite operation does not restore? `status` derives `collateral` and `debt` flags from bit tests against whatever mask it was handed, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:115` -> `status`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `status` derives `collateral` and `debt` flags from bit tests against whatever mask it was handed. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the order of accrual versus price resolution inside the let varied, and assert that the value `status` returns is identical in both runs; a divergence confirms the finding.

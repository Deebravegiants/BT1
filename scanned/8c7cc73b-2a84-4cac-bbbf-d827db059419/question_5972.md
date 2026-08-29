# Q5972: lookup via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `lookup` (mainnet/contracts/registry/v0-assets.clar:139) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it returns the registry record, including the `decimals` captured once at registration, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `lookup` returns is identical in both runs; a divergence confirms the finding.

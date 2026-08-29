# Q2144: collateral-add via repay: credit one side of an accounting pair without the other

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `on-behalf-of`, naming any third-party principal reach `collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) in a state where it credit one side of an accounting pair without the other? Given that it evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `on-behalf-of`, naming any third-party principal varied, and assert that the value `collateral-add` returns is identical in both runs; a divergence confirms the finding.

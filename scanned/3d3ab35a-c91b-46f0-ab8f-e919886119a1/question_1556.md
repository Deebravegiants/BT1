# Q1556: get-egroup via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) in a state where it count one deposit as backing for two simultaneous claims? Given that it resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `min-underlying` varied, and assert that the value `get-egroup` returns is identical in both runs; a divergence confirms the finding.

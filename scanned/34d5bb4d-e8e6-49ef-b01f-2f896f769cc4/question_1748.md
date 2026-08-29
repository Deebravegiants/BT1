# Q1748: find via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `ft` trait principal reach `find` (mainnet/contracts/registry/v0-assets.clar:135) in a state where it count one deposit as backing for two simultaneous claims? Given that it resolves an asset record from a principal through the `reverse` map, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the `ft` trait principal varied, and assert that the value `find` returns is identical in both runs; a divergence confirms the finding.

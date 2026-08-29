# Q5762: filter-u128 via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the `ft` trait principal, can an unprivileged attacker make `filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) count one deposit as backing for two simultaneous claims? `filter-u128` filters a 128-entry bucket list, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the `ft` trait principal varied, and assert that the value `filter-u128` returns is identical in both runs; a divergence confirms the finding.

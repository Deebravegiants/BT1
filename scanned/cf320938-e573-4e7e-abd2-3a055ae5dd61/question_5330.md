# Q5330: price-multi-resolve via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the position state the final collateral-add is validated against, can an unprivileged attacker make `price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) count one deposit as backing for two simultaneous claims? `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with the position state the final collateral-add is validated against varied, and assert that the value `price-multi-resolve` returns is identical in both runs; a divergence confirms the finding.

# Q5570: iter-find-superset via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `amount` relative to the current collateral row (the removing-all branch), can an unprivileged attacker make `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) count one deposit as backing for two simultaneous claims? `iter-find-superset` short-circuits on the first superset match, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `amount` relative to the current collateral row (the removing-all branch) varied, and assert that the value `iter-find-superset` returns is identical in both runs; a divergence confirms the finding.

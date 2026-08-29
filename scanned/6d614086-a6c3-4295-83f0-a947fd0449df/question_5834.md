# Q5834: get-egroup via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `amount` relative to the current collateral row (the removing-all branch), can an unprivileged attacker make `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) count one deposit as backing for two simultaneous claims? `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `amount` relative to the current collateral row (the removing-all branch) varied, and assert that the value `get-egroup` returns is identical in both runs; a divergence confirms the finding.

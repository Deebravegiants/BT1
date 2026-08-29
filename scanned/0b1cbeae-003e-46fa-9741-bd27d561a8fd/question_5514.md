# Q5514: mask-update via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling the zToken/underlying id mapping reached (the u100 sentinel branch), can an unprivileged attacker make `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) count one deposit as backing for two simultaneous claims? `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the zToken/underlying id mapping reached (the u100 sentinel branch) across its boundary values through `collateral-remove-redeem` in simnet and assert `mask-update` never returns a value that breaks the invariant.

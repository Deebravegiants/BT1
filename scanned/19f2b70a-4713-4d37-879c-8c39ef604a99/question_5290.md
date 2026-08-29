# Q5290: unpack-u16 via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the position state the final collateral-add is validated against, can an unprivileged attacker make `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) count one deposit as backing for two simultaneous claims? `unpack-u16` unpacks eight u16 curve fields from one packed word, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with the position state the final collateral-add is validated against, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.

# Q5778: send-tokens via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the `ft` trait principal deciding which vault is routed to, can an unprivileged attacker make `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) count one deposit as backing for two simultaneous claims? `send-tokens` pushes an asset to a caller-chosen recipient principal, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `ft` trait principal deciding which vault is routed to across its boundary values through `supply-collateral-add` in simnet and assert `send-tokens` never returns a value that breaks the invariant.

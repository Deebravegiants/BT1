# Q3891: calc-principal-ratio-reduction via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
`calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) reduces scaled principal proportionally to an amount over total debt. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing vault share price at the moment of the deposit leg, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-principal-ratio-reduction` touches, run `supply-collateral-add` with vault share price at the moment of the deposit leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

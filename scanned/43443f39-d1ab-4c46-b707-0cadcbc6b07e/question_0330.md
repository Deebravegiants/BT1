# Q0330: oracle-price-legal via supply-collateral-add: mint shares whose backing was never received

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the position state the final collateral-add is validated against, can an unprivileged attacker make `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) mint shares whose backing was never received? `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the position state the final collateral-add is validated against across its boundary values through `supply-collateral-add` in simnet and assert `oracle-price-legal` never returns a value that breaks the invariant.

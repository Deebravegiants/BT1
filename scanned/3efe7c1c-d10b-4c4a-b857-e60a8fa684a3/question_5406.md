# Q5406: find-and-resolve-asset-value via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling whether this asset is already collateral (the is-new-collateral branch), can an unprivileged attacker make `find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) count one deposit as backing for two simultaneous claims? `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz whether this asset is already collateral (the is-new-collateral branch) across its boundary values through `collateral-add` in simnet and assert `find-and-resolve-asset-value` never returns a value that breaks the invariant.

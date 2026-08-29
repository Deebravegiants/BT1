# Q5358: increment via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling whether this asset is already collateral (the is-new-collateral branch), can an unprivileged attacker make `increment` (mainnet/contracts/market/v0-market-vault.clar:137) count one deposit as backing for two simultaneous claims? `increment` advances the user-id nonce, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `increment` advances the user-id nonce. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether this asset is already collateral (the is-new-collateral branch) across its boundary values through `collateral-add` in simnet and assert `increment` never returns a value that breaks the invariant.

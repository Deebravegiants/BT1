# Q5454: oracle-last-update via liquidate: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) count one deposit as backing for two simultaneous claims? `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `oracle-last-update` never returns a value that breaks the invariant.

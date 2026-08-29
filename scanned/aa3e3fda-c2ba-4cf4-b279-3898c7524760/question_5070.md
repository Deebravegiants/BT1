# Q5070: mask-to-list-collateral via liquidate: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `mask-to-list-collateral` (mainnet/contracts/market/v0-4-market.clar:449) count one deposit as backing for two simultaneous claims? `mask-to-list-collateral` expands a mask to a list of ids over ITER-UINT-64, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:449` -> `mask-to-list-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `mask-to-list-collateral` expands a mask to a list of ids over ITER-UINT-64. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `mask-to-list-collateral` never returns a value that breaks the invariant.

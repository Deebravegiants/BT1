# Q5862: get-full-position via liquidate: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) count one deposit as backing for two simultaneous claims? `get-full-position` returns all collateral rows regardless of the enabled bitmap, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `get-full-position` never returns a value that breaks the invariant.

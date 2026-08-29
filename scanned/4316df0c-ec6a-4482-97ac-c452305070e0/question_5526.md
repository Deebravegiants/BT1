# Q5526: resolve-ststx via liquidate: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `resolve-ststx` (mainnet/contracts/market/v0-4-market.clar:339) count one deposit as backing for two simultaneous claims? `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:339` -> `resolve-ststx`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `resolve-ststx` never returns a value that breaks the invariant.

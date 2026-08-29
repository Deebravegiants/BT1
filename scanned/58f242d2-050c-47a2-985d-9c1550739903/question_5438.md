# Q5438: get-position via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `receiver` for the underlying leg, can an unprivileged attacker make `get-position` (mainnet/contracts/market/v0-4-market.clar:466) count one deposit as backing for two simultaneous claims? `get-position` returns only rows whose bit is set in the ENABLED bitmap, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `receiver` for the underlying leg varied, and assert that the value `get-position` returns is identical in both runs; a divergence confirms the finding.

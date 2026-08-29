# Q5582: convert-to-scaled-debt via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `min-underlying`, can an unprivileged attacker make `convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) count one deposit as backing for two simultaneous claims? `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `min-underlying` varied, and assert that the value `convert-to-scaled-debt` returns is identical in both runs; a divergence confirms the finding.

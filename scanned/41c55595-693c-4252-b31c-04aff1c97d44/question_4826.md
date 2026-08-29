# Q4826: get-full-position via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling remaining zToken collateral whose price moves with the redeem, can an unprivileged attacker make `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) destroy value through a truncation the opposite operation does not restore? `get-full-position` returns all collateral rows regardless of the enabled bitmap, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with remaining zToken collateral whose price moves with the redeem varied, and assert that the value `get-full-position` returns is identical in both runs; a divergence confirms the finding.

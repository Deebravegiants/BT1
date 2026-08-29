# Q4338: mask-pos via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) destroy value through a truncation the opposite operation does not restore? `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `mask-pos` never returns a value that breaks the invariant.

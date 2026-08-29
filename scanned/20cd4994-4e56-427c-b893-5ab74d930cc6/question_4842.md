# Q4842: find-collateral-amount via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) destroy value through a truncation the opposite operation does not restore? `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `find-collateral-amount` never returns a value that breaks the invariant.

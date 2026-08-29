# Q4074: calc-liq-collateral-repay via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `calc-liq-collateral-repay` (mainnet/contracts/market/v0-4-market.clar:728) destroy value through a truncation the opposite operation does not restore? `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:728` -> `calc-liq-collateral-repay`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `calc-liq-collateral-repay` never returns a value that breaks the invariant.

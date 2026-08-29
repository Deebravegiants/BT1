# Q4722: get-full-position via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) destroy value through a truncation the opposite operation does not restore? `get-full-position` returns all collateral rows regardless of the enabled bitmap, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the redemption receiver across its boundary values through `liquidate-redeem` in simnet and assert `get-full-position` never returns a value that breaks the invariant.

# Q3474: accrue-collateral-asset via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the seized zToken amount that is immediately redeemed, can an unprivileged attacker make `accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) leave a residue that no reconciliation pass ever inspects? `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the seized zToken amount that is immediately redeemed across its boundary values through `liquidate-redeem` in simnet and assert `accrue-collateral-asset` never returns a value that breaks the invariant.

# Q3362: find-collateral-amount via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the seized zToken amount that is immediately redeemed, can an unprivileged attacker make `find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) leave a residue that no reconciliation pass ever inspects? `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the seized zToken amount that is immediately redeemed varied, and assert that the value `find-collateral-amount` returns is identical in both runs; a divergence confirms the finding.

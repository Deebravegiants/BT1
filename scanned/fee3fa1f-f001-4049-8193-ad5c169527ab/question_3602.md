# Q3602: get-liquidation-position via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) leave a residue that no reconciliation pass ever inspects? `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `get-liquidation-position` returns is identical in both runs; a divergence confirms the finding.

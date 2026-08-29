# Q3306: get-account-scaled-debt via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `min-collateral-expected`, can an unprivileged attacker make `get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) leave a residue that no reconciliation pass ever inspects? `get-account-scaled-debt` reads one scaled debt row, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `get-account-scaled-debt` never returns a value that breaks the invariant.

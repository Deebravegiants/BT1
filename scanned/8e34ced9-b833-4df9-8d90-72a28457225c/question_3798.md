# Q3798: find-debt-scaled via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `find-debt-scaled` (mainnet/contracts/market/v0-4-market.clar:621) leave a residue that no reconciliation pass ever inspects? `find-debt-scaled` returns u0 for an absent asset, making a missing debt row indistinguishable from no debt, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:621` -> `find-debt-scaled`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `find-debt-scaled` returns u0 for an absent asset, making a missing debt row indistinguishable from no debt. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the three `price-feeds` buffers and their order across its boundary values through `collateral-add` in simnet and assert `find-debt-scaled` never returns a value that breaks the invariant.

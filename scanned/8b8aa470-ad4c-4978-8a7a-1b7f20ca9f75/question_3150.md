# Q3150: mask-update via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `min-collateral-expected`, can an unprivileged attacker make `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) leave a residue that no reconciliation pass ever inspects? `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `mask-update` never returns a value that breaks the invariant.

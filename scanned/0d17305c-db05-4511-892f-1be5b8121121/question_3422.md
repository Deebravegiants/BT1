# Q3422: interpolate-rate via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) leave a residue that no reconciliation pass ever inspects? `interpolate-rate` interpolates between packed u16 curve points, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with which collateral and debt asset pair is targeted varied, and assert that the value `interpolate-rate` returns is identical in both runs; a divergence confirms the finding.

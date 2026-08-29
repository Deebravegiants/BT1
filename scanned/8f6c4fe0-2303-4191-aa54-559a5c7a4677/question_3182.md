# Q3182: oracle-last-update via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) leave a residue that no reconciliation pass ever inspects? `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `oracle-last-update` returns is identical in both runs; a divergence confirms the finding.

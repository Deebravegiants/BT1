# Q3134: linear-interpolate via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) leave a residue that no reconciliation pass ever inspects? `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `linear-interpolate` returns is identical in both runs; a divergence confirms the finding.

# Q3806: add-user-collateral via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) leave a residue that no reconciliation pass ever inspects? `add-user-collateral` adds to the collateral row with a graceful u0 default, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `add-user-collateral` returns is identical in both runs; a divergence confirms the finding.

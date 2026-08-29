# Q3350: remove-user-scaled-debt via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the future mask produced by the new debt bit, can an unprivileged attacker make `remove-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:244) leave a residue that no reconciliation pass ever inspects? `remove-user-scaled-debt` deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:244` -> `remove-user-scaled-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `remove-user-scaled-debt` deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the future mask produced by the new debt bit varied, and assert that the value `remove-user-scaled-debt` returns is identical in both runs; a divergence confirms the finding.

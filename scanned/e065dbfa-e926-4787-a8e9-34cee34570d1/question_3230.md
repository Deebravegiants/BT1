# Q3230: resolve-dia via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the seized zToken amount that is immediately redeemed, can an unprivileged attacker make `resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) leave a residue that no reconciliation pass ever inspects? `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the seized zToken amount that is immediately redeemed varied, and assert that the value `resolve-dia` returns is identical in both runs; a divergence confirms the finding.

# Q1459: resolve-dia via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
`resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) derives a (string-ascii 32) key from a (buff 32) ident. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the trait principals supplied per entry, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with the trait principals supplied per entry, then read `resolve-dia` state before and after in the same block and assert the two sides of the invariant are equal.

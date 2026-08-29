# Q5809: vault-socialize-debt via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling the `price-feeds` buffers and their ordering, drive `vault-socialize-debt` (mainnet/contracts/market/v0-4-market.clar:216) — which routes a scaled write-down to one of six vaults — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:216` -> `vault-socialize-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `vault-socialize-debt` routes a scaled write-down to one of six vaults. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with the `price-feeds` buffers and their ordering, then read `vault-socialize-debt` state before and after in the same block and assert the two sides of the invariant are equal.

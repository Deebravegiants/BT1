# Q5785: calc-liq-factor-bound via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling the `price-feeds` buffers and their ordering, drive `calc-liq-factor-bound` (mainnet/contracts/market/v0-4-market.clar:718) — which scales the penalty between a min and a max, capped at the max — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:718` -> `calc-liq-factor-bound`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `calc-liq-factor-bound` scales the penalty between a min and a max, capped at the max. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with the `price-feeds` buffers and their ordering, then read `calc-liq-factor-bound` state before and after in the same block and assert the two sides of the invariant are equal.

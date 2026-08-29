# Q5233: remove-user-scaled-debt via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling how many entries share one price snapshot (price-feeds is passed as none), drive `remove-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:244) — which deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:244` -> `remove-user-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `remove-user-scaled-debt` deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with how many entries share one price snapshot (price-feeds is passed as none), then read `remove-user-scaled-debt` state before and after in the same block and assert the two sides of the invariant are equal.

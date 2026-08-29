# Q5049: interpolate-rate via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling `amount`, drive `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) — which interpolates between packed u16 curve points — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `interpolate-rate` touches, run `collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

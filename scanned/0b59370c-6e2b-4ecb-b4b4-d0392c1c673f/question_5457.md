# Q5457: subset via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling `amount`, drive `subset` (mainnet/contracts/market/v0-market-vault.clar:100) — which tests bitmask containment — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `subset` tests bitmask containment. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `subset` touches, run `collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

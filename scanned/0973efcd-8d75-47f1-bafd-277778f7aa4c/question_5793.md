# Q5793: accrue-user-collateral via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `debt-amount`, drive `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) — which accrues only rows that `is-ztoken` recognises, skipping everything else — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `accrue-user-collateral` touches, run `liquidate` with `debt-amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

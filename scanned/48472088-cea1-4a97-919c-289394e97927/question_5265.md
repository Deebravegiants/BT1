# Q5265: calc-treasury-lp-preview via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling `amount`, drive `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) — which divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-treasury-lp-preview` touches, run `transfer` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

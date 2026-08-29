# Q5433: debt-preview via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling `recipient`, including a contract principal, drive `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) — which computes cumulative debt from `principal-scaled` and the FORWARD index — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `debt-preview` touches, run `deposit` with `recipient`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

# Q5721: uint-to-list-u64 via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `receiver`, including a contract principal, drive `uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) — which expands a bitmap into a 64-element list — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `uint-to-list-u64` touches, run `borrow` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.

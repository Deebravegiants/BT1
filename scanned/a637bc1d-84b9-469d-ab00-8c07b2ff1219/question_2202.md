# Q2202: uint-to-list-u64 via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) have the same quantity scaled twice by two contracts that round differently? `uint-to-list-u64` expands a bitmap into a 64-element list, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `collateral-remove` in simnet and assert `uint-to-list-u64` never returns a value that breaks the invariant.

# Q3143: resolve via borrow: count one deposit as backing for two simultaneous claims

## Question
`resolve` (mainnet/contracts/registry/v0-egroup.clar:360) selects the efficiency group for a position mask. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `receiver`, including a contract principal, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:360` -> `resolve`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `resolve` selects the efficiency group for a position mask. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `receiver`, including a contract principal, and assert the attacker's net token balance change is zero or negative.

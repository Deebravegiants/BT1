# Q3239: insert via borrow: count one deposit as backing for two simultaneous claims

## Question
`insert` (mainnet/contracts/market/v0-market-vault.clar:159) rewrites the whole registry entry for a user id. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `receiver`, including a contract principal, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `receiver`, including a contract principal, and assert the attacker's net token balance change is zero or negative.

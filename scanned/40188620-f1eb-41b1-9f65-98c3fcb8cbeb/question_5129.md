# Q5129: increment via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the `price-feeds` buffers, drive `increment` (mainnet/contracts/market/v0-market-vault.clar:137) — which advances the user-id nonce — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `increment` advances the user-id nonce. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the `price-feeds` buffers, and assert the attacker's net token balance change is zero or negative.

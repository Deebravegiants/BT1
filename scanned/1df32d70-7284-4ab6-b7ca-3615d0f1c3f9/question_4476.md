# Q4476: zip via borrow: mint shares whose backing was never received

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `price-feeds` buffers reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it mint shares whose backing was never received? Given that it pairs the utilization and rate point lists element by element, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `borrow` in simnet and assert `zip` never returns a value that breaks the invariant.

# Q295: Public-call brick via deposit under two account ping heavy dust threshold

## Question
Can an unprivileged attacker compose valid public calls around `staking-pool/src/lib.rs::deposit()` with two attacker EOAs alternating calls to compare split and merged positions and a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step, so the pool reaches a state where `internal_ping()` or a later public method reliably panics on invariant checks and honest users can no longer settle rewards, unstake, or withdraw?

## Target
- File/function: `staking-pool/src/lib.rs::deposit` with `staking-pool/src/internal.rs::internal_deposit` and `staking-pool/src/internal.rs::internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and assertion-based state transitions
- Entrypoint: `staking-pool/src/lib.rs::deposit()`
- Attacker controls: attached deposit size, number of attacker accounts, follow-up call ordering, and epoch timing; two attacker EOAs alternating calls to compare split and merged positions; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Look for a sequence where user-triggered accounting deltas make a later assertion on `last_total_balance`, total shares, or total stake unsatisfiable without privileged repair.
- Invariant to test: Any state reachable solely through valid public methods must remain serviceable by later valid public methods and must not permanently freeze user funds.
- Expected Immunefi impact: Contracts execution flows
- Fast validation: Stateful fuzzing over all public user calls with `staking-pool/src/lib.rs::deposit()` emphasized; stop on any sequence that causes all future `ping()/unstake()/withdraw()` attempts to panic.

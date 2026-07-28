# Q315: Public-call brick via deposit under helper contract epoch boundary dust threshold

## Question
Can an unprivileged attacker compose valid public calls around `staking-pool/src/lib.rs::deposit()` with an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits and the attacker straddles an epoch transition where the pool has a small positive reward to settle, so the pool reaches a state where `internal_ping()` or a later public method reliably panics on invariant checks and honest users can no longer settle rewards, unstake, or withdraw?

## Target
- File/function: `staking-pool/src/lib.rs::deposit` with `staking-pool/src/internal.rs::internal_deposit` and `staking-pool/src/internal.rs::internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and assertion-based state transitions
- Entrypoint: `staking-pool/src/lib.rs::deposit()`
- Attacker controls: attached deposit size, number of attacker accounts, follow-up call ordering, and epoch timing; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; the attacker straddles an epoch transition where the pool has a small positive reward to settle; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Look for a sequence where user-triggered accounting deltas make a later assertion on `last_total_balance`, total shares, or total stake unsatisfiable without privileged repair.
- Invariant to test: Any state reachable solely through valid public methods must remain serviceable by later valid public methods and must not permanently freeze user funds.
- Expected Immunefi impact: Contracts execution flows
- Fast validation: Stateful fuzzing over all public user calls with `staking-pool/src/lib.rs::deposit()` emphasized; stop on any sequence that causes all future `ping()/unstake()/withdraw()` attempts to panic.

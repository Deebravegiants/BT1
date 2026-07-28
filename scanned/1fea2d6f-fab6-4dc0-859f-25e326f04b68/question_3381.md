# Q3381: Public-call brick via withdraw_all under many account unlock boundary dust threshold

## Question
Can an unprivileged attacker compose valid public calls around `staking-pool/src/lib.rs::withdraw_all()` with sixteen attacker EOAs splitting the same total capital into many dust positions and the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking, so the pool reaches a state where `internal_ping()` or a later public method reliably panics on invariant checks and honest users can no longer settle rewards, unstake, or withdraw?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw_all` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and assertion-based state transitions
- Entrypoint: `staking-pool/src/lib.rs::withdraw_all()`
- Attacker controls: full unstaked balance, epoch height, intervening `ping()` calls, and whether dust or extra liquid value remains after full withdrawal; sixteen attacker EOAs splitting the same total capital into many dust positions; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Look for a sequence where user-triggered accounting deltas make a later assertion on `last_total_balance`, total shares, or total stake unsatisfiable without privileged repair.
- Invariant to test: Any state reachable solely through valid public methods must remain serviceable by later valid public methods and must not permanently freeze user funds.
- Expected Immunefi impact: Contracts execution flows
- Fast validation: Stateful fuzzing over all public user calls with `staking-pool/src/lib.rs::withdraw_all()` emphasized; stop on any sequence that causes all future `ping()/unstake()/withdraw()` attempts to panic.

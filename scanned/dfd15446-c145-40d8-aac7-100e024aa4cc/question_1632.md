# Q1632: Public-call brick via stake_all under victim pair ping heavy full position edge

## Question
Can an unprivileged attacker compose valid public calls around `staking-pool/src/lib.rs::stake_all()` with one attacker EOA acting against a passive victim account that is already staked and a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step, so the pool reaches a state where `internal_ping()` or a later public method reliably panics on invariant checks and honest users can no longer settle rewards, unstake, or withdraw?

## Target
- File/function: `staking-pool/src/lib.rs::stake_all` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and assertion-based state transitions
- Entrypoint: `staking-pool/src/lib.rs::stake_all()`
- Attacker controls: pre-existing unstaked balance, account splits, reward timing, and whether full-position conversion leaves dust; one attacker EOA acting against a passive victim account that is already staked; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Look for a sequence where user-triggered accounting deltas make a later assertion on `last_total_balance`, total shares, or total stake unsatisfiable without privileged repair.
- Invariant to test: Any state reachable solely through valid public methods must remain serviceable by later valid public methods and must not permanently freeze user funds.
- Expected Immunefi impact: Contracts execution flows
- Fast validation: Stateful fuzzing over all public user calls with `staking-pool/src/lib.rs::stake_all()` emphasized; stop on any sequence that causes all future `ping()/unstake()/withdraw()` attempts to panic.

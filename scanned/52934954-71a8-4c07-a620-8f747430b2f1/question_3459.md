# Q3459: Permanent dust lock via withdraw_all under many account epoch boundary dust threshold

## Question
Can an unprivileged attacker or a passive victim be pushed through `staking-pool/src/lib.rs::withdraw_all()` with dust-sized values near the smallest amount that still mints nonzero shares or changes rounding and the attacker straddles an epoch transition where the pool has a small positive reward to settle into a state where nonzero value remains permanently stranded as unstakable shares or unwithdrawable dust, even though the position should be economically empty?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw_all` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, `internal_withdraw`, and per-account balances
- Entrypoint: `staking-pool/src/lib.rs::withdraw_all()`
- Attacker controls: full unstaked balance, epoch height, intervening `ping()` calls, and whether dust or extra liquid value remains after full withdrawal; sixteen attacker EOAs splitting the same total capital into many dust positions; the attacker straddles an epoch transition where the pool has a small positive reward to settle; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Search for one-yocto or one-share remnants created by `staking-pool/src/lib.rs::withdraw_all()` that no later valid public call can recover.
- Invariant to test: Any residual balance created by honest public use must remain eventually recoverable, and one user should not be able to strand another user's funds in unrecoverable dust.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Sweep tiny amounts through deposit/stake/unstake/withdraw sequences centered on `staking-pool/src/lib.rs::withdraw_all()`; assert that every positive residual can either be staked, unstaked, or withdrawn in finite public steps.

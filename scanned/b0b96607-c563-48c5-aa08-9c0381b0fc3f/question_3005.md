# Q3005: Permanent dust lock via withdraw under single account unlock boundary dust threshold

## Question
Can an unprivileged attacker or a passive victim be pushed through `staking-pool/src/lib.rs::withdraw()` with dust-sized values near the smallest amount that still mints nonzero shares or changes rounding and the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking into a state where nonzero value remains permanently stranded as unstakable shares or unwithdrawable dust, even though the position should be economically empty?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, `internal_withdraw`, and per-account balances
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; one attacker EOA controlling a single staking position; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Search for one-yocto or one-share remnants created by `staking-pool/src/lib.rs::withdraw()` that no later valid public call can recover.
- Invariant to test: Any residual balance created by honest public use must remain eventually recoverable, and one user should not be able to strand another user's funds in unrecoverable dust.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Sweep tiny amounts through deposit/stake/unstake/withdraw sequences centered on `staking-pool/src/lib.rs::withdraw()`; assert that every positive residual can either be staked, unstaked, or withdrawn in finite public steps.

# Q1241: Permanent dust lock via stake under single account same epoch dust threshold

## Question
Can an unprivileged attacker or a passive victim be pushed through `staking-pool/src/lib.rs::stake()` with dust-sized values near the smallest amount that still mints nonzero shares or changes rounding and all attacker-visible steps happen in the same epoch before any natural reward settlement into a state where nonzero value remains permanently stranded as unstakable shares or unwithdrawable dust, even though the position should be economically empty?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, `internal_withdraw`, and per-account balances
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; one attacker EOA controlling a single staking position; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Search for one-yocto or one-share remnants created by `staking-pool/src/lib.rs::stake()` that no later valid public call can recover.
- Invariant to test: Any residual balance created by honest public use must remain eventually recoverable, and one user should not be able to strand another user's funds in unrecoverable dust.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Sweep tiny amounts through deposit/stake/unstake/withdraw sequences centered on `staking-pool/src/lib.rs::stake()`; assert that every positive residual can either be staked, unstaked, or withdrawn in finite public steps.

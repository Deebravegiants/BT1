# Q2135: Permanent dust lock via unstake under two account ping heavy dust threshold

## Question
Can an unprivileged attacker or a passive victim be pushed through `staking-pool/src/lib.rs::unstake()` with dust-sized values near the smallest amount that still mints nonzero shares or changes rounding and a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step into a state where nonzero value remains permanently stranded as unstakable shares or unwithdrawable dust, even though the position should be economically empty?

## Target
- File/function: `staking-pool/src/lib.rs::unstake` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, `internal_withdraw`, and per-account balances
- Entrypoint: `staking-pool/src/lib.rs::unstake()`
- Attacker controls: unstake amount, existing share balance, epoch boundary, and post-unstake withdrawal timing; two attacker EOAs alternating calls to compare split and merged positions; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Search for one-yocto or one-share remnants created by `staking-pool/src/lib.rs::unstake()` that no later valid public call can recover.
- Invariant to test: Any residual balance created by honest public use must remain eventually recoverable, and one user should not be able to strand another user's funds in unrecoverable dust.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Sweep tiny amounts through deposit/stake/unstake/withdraw sequences centered on `staking-pool/src/lib.rs::unstake()`; assert that every positive residual can either be staked, unstaked, or withdrawn in finite public steps.

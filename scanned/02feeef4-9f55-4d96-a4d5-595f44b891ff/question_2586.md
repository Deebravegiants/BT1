# Q2586: Permanent dust lock via unstake_all under victim pair same epoch full position edge

## Question
Can an unprivileged attacker or a passive victim be pushed through `staking-pool/src/lib.rs::unstake_all()` with near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge and all attacker-visible steps happen in the same epoch before any natural reward settlement into a state where nonzero value remains permanently stranded as unstakable shares or unwithdrawable dust, even though the position should be economically empty?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, `internal_withdraw`, and per-account balances
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; one attacker EOA acting against a passive victim account that is already staked; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Search for one-yocto or one-share remnants created by `staking-pool/src/lib.rs::unstake_all()` that no later valid public call can recover.
- Invariant to test: Any residual balance created by honest public use must remain eventually recoverable, and one user should not be able to strand another user's funds in unrecoverable dust.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Sweep tiny amounts through deposit/stake/unstake/withdraw sequences centered on `staking-pool/src/lib.rs::unstake_all()`; assert that every positive residual can either be staked, unstaked, or withdrawn in finite public steps.

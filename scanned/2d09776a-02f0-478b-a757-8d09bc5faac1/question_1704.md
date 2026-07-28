# Q1704: Permanent dust lock via stake_all under many account ping heavy full position edge

## Question
Can an unprivileged attacker or a passive victim be pushed through `staking-pool/src/lib.rs::stake_all()` with near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge and a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step into a state where nonzero value remains permanently stranded as unstakable shares or unwithdrawable dust, even though the position should be economically empty?

## Target
- File/function: `staking-pool/src/lib.rs::stake_all` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, `internal_withdraw`, and per-account balances
- Entrypoint: `staking-pool/src/lib.rs::stake_all()`
- Attacker controls: pre-existing unstaked balance, account splits, reward timing, and whether full-position conversion leaves dust; sixteen attacker EOAs splitting the same total capital into many dust positions; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Search for one-yocto or one-share remnants created by `staking-pool/src/lib.rs::stake_all()` that no later valid public call can recover.
- Invariant to test: Any residual balance created by honest public use must remain eventually recoverable, and one user should not be able to strand another user's funds in unrecoverable dust.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Sweep tiny amounts through deposit/stake/unstake/withdraw sequences centered on `staking-pool/src/lib.rs::stake_all()`; assert that every positive residual can either be staked, unstaked, or withdrawn in finite public steps.

# Q1234: Owner-fee bypass via stake under helper contract same epoch full position edge

## Question
Can an unprivileged attacker time `staking-pool/src/lib.rs::stake()` with all attacker-visible steps happen in the same epoch before any natural reward settlement and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge so reward settlement occurs while the attacker is in or out of the pool at precisely the profitable moment, effectively bypassing the intended owner fee or making other stakers absorb a larger fee share than the attacker's capital should bear?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_ping` and owner-fee share minting in `reward_fee_fraction.multiply(total_reward)`
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Test whether the public call order around `internal_ping()` lets the attacker enter after fee dilution but exit before bearing the matching fee-adjusted economics.
- Invariant to test: Owner fee should be collected proportionally from the rewarded stake base, and public settlement timing must not let one user offload that fee burden onto others.
- Expected Immunefi impact: Fee payment bypass
- Fast validation: Run paired simulations with the same reward and stake set, varying only whether `staking-pool/src/lib.rs::stake()` happens before or after `ping()`; compare attacker net value and owner fee collected.

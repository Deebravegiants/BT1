# Q2989: Owner-fee bypass via withdraw under victim pair unlock boundary dust threshold

## Question
Can an unprivileged attacker time `staking-pool/src/lib.rs::withdraw()` with the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding so reward settlement occurs while the attacker is in or out of the pool at precisely the profitable moment, effectively bypassing the intended owner fee or making other stakers absorb a larger fee share than the attacker's capital should bear?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping` and owner-fee share minting in `reward_fee_fraction.multiply(total_reward)`
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; one attacker EOA acting against a passive victim account that is already staked; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Test whether the public call order around `internal_ping()` lets the attacker enter after fee dilution but exit before bearing the matching fee-adjusted economics.
- Invariant to test: Owner fee should be collected proportionally from the rewarded stake base, and public settlement timing must not let one user offload that fee burden onto others.
- Expected Immunefi impact: Fee payment bypass
- Fast validation: Run paired simulations with the same reward and stake set, varying only whether `staking-pool/src/lib.rs::withdraw()` happens before or after `ping()`; compare attacker net value and owner fee collected.

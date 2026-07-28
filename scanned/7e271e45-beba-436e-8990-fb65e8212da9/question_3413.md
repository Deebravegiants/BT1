# Q3413: Owner-fee bypass via withdraw_all under two account unlock boundary dust threshold

## Question
Can an unprivileged attacker time `staking-pool/src/lib.rs::withdraw_all()` with the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding so reward settlement occurs while the attacker is in or out of the pool at precisely the profitable moment, effectively bypassing the intended owner fee or making other stakers absorb a larger fee share than the attacker's capital should bear?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw_all` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping` and owner-fee share minting in `reward_fee_fraction.multiply(total_reward)`
- Entrypoint: `staking-pool/src/lib.rs::withdraw_all()`
- Attacker controls: full unstaked balance, epoch height, intervening `ping()` calls, and whether dust or extra liquid value remains after full withdrawal; two attacker EOAs alternating calls to compare split and merged positions; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Test whether the public call order around `internal_ping()` lets the attacker enter after fee dilution but exit before bearing the matching fee-adjusted economics.
- Invariant to test: Owner fee should be collected proportionally from the rewarded stake base, and public settlement timing must not let one user offload that fee burden onto others.
- Expected Immunefi impact: Fee payment bypass
- Fast validation: Run paired simulations with the same reward and stake set, varying only whether `staking-pool/src/lib.rs::withdraw_all()` happens before or after `ping()`; compare attacker net value and owner fee collected.

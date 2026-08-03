# Q1505: payout_stakers can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `payout_stakers` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `Ledger` / `Nominators`?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::payout_stakers
- Entrypoint: signed extrinsic `payout_stakers`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

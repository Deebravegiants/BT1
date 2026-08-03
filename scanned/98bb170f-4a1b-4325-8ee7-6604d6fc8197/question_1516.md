# Q1516: vest_other can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `vest_other` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `Vesting` / `free balance`?

## Target
- File/function: substrate/frame/vesting/src/lib.rs::vest_other
- Entrypoint: signed extrinsic `vest_other`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

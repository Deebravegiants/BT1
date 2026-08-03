# Q1510: set_payee can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `set_payee` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `Ledger` / `Nominators`?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::set_payee
- Entrypoint: signed extrinsic `set_payee`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

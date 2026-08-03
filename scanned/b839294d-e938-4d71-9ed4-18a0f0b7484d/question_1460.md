# Q1460: partition can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `partition` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `Regions` / `Workplan`?

## Target
- File/function: substrate/frame/broker/src/lib.rs::partition
- Entrypoint: signed extrinsic `partition`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

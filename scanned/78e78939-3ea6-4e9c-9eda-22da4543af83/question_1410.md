# Q1410: harvest_rewards can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `harvest_rewards` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `Pools` / `PoolStakers`?

## Target
- File/function: substrate/frame/asset-rewards/src/lib.rs::harvest_rewards
- Entrypoint: signed extrinsic `harvest_rewards`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

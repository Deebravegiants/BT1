# Q1494: update_roles can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `update_roles` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `BondedPools` / `PoolMembers`?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::update_roles
- Entrypoint: signed extrinsic `update_roles`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

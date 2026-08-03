# Q1426: refund_other can bypass hold, lock, or freeze semantics

## Question
Can an unprivileged attacker combine `refund_other` with ordinary public flows to move value that should still be locked, frozen, delegated, or slashable under `AssetDetails` / `Accounts`?

## Target
- File/function: substrate/frame/assets/src/lib.rs::refund_other
- Entrypoint: signed extrinsic `refund_other`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Look for paths that read spendable state from one ledger while another still treats the same value as encumbered.
- Invariant to test: Locked or frozen value must not become transferable, withdrawable, or claimable until every governing ledger agrees it is free.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Stage value under every relevant hold/freeze/vesting/slash condition and assert no spendable escape hatch appears.

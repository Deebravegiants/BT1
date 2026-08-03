# Q1786: set_primary_username can expose underpriced public auth work

## Question
Can an unprivileged attacker use `set_primary_username` to force underpriced scans or persistence of public auth records, degrading block production or storage growth in an in-scope way?

## Target
- File/function: substrate/frame/identity/src/lib.rs::set_primary_username
- Entrypoint: signed extrinsic `set_primary_username`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for public loops over announcements, multisig approvals, friend groups, sub-accounts, or preimages.
- Invariant to test: Worst-case public auth maintenance work must remain within charged weight and storage limits.
- Expected Immunefi impact: State corruption or underpriced wrapped execution leading to chain degradation
- Fast validation: Fuzz maximum pending records, duplicate-heavy inputs, and repeated partial cleanups.

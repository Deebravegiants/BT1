# Q1794: ensure_updated can expose underpriced public auth work

## Question
Can an unprivileged attacker use `ensure_updated` to force underpriced scans or persistence of public auth records, degrading block production or storage growth in an in-scope way?

## Target
- File/function: substrate/frame/preimage/src/lib.rs::ensure_updated
- Entrypoint: signed extrinsic `ensure_updated`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Look for public loops over announcements, multisig approvals, friend groups, sub-accounts, or preimages.
- Invariant to test: Worst-case public auth maintenance work must remain within charged weight and storage limits.
- Expected Immunefi impact: State corruption or underpriced wrapped execution leading to chain degradation
- Fast validation: Fuzz maximum pending records, duplicate-heavy inputs, and repeated partial cleanups.

# Q2048: create_pure can leave stale mappings after subject changes

## Question
Can an unprivileged attacker use `create_pure` near a rename, revoke, recovery, or authority change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::create_pure
- Entrypoint: public dispatch wrapper `create_pure`
- Attacker controls: IDs, hashes, nonces, or location fields, batched or wrapped execution context
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

# Q2035: set_primary_username can leave stale mappings after subject changes

## Question
Can an unprivileged attacker use `set_primary_username` near a rename, revoke, recovery, or authority change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/identity/src/lib.rs::set_primary_username
- Entrypoint: signed extrinsic `set_primary_username`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

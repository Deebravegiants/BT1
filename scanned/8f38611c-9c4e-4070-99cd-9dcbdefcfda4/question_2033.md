# Q2033: request_judgement can leave stale mappings after subject changes

## Question
Can an unprivileged attacker use `request_judgement` near a rename, revoke, recovery, or authority change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/identity/src/lib.rs::request_judgement
- Entrypoint: signed extrinsic `request_judgement`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

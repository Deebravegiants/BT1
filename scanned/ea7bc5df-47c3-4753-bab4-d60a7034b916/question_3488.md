# Q3488: remove_vote can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `remove_vote` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/conviction-voting/src/lib.rs::remove_vote
- Entrypoint: signed extrinsic `remove_vote`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

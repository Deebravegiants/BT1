# Q3478: force_transfer can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `force_transfer` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::force_transfer
- Entrypoint: signed extrinsic `force_transfer`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

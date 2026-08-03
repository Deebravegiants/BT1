# Q3454: clear_all_transfer_approvals can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `clear_all_transfer_approvals` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::clear_all_transfer_approvals
- Entrypoint: signed extrinsic `clear_all_transfer_approvals`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

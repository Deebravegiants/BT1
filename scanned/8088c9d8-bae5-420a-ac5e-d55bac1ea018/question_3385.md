# Q3385: set_commission_max can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `set_commission_max` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::set_commission_max
- Entrypoint: signed extrinsic `set_commission_max`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

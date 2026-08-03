# Q3372: bond_extra_other can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `bond_extra_other` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::bond_extra_other
- Entrypoint: signed extrinsic `bond_extra_other`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

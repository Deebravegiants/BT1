# Q3356: drop_history can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `drop_history` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/broker/src/lib.rs::drop_history
- Entrypoint: signed extrinsic `drop_history`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

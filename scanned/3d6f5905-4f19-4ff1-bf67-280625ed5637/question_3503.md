# Q3503: reap_page can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `reap_page` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::reap_page
- Entrypoint: public message maintenance extrinsic `reap_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

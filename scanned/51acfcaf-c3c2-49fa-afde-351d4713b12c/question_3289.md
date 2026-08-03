# Q3289: submit_delivery_receipt can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `submit_delivery_receipt` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: bridges/snowbridge/pallets/outbound-queue-v2/src/lib.rs::submit_delivery_receipt
- Entrypoint: public proof / message submission extrinsic `submit_delivery_receipt`
- Attacker controls: proof or signed payload contents
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

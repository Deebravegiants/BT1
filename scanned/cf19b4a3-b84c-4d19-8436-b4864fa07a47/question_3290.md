# Q3290: call can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `call` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::call
- Entrypoint: public VM / contract execution extrinsic `call`
- Attacker controls: nested call payloads, amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.

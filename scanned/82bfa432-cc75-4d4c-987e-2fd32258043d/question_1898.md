# Q1898: execute_overweight can confuse page, index, or origin binding

## Question
Can an unprivileged attacker use `execute_overweight` with crafted IDs, hashes, nonces, or location fields so the runtime operates on the wrong page, index, or message origin?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::execute_overweight
- Entrypoint: public message maintenance extrinsic `execute_overweight`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe aliasing and boundary checks for page, index, and origin identifiers.
- Invariant to test: Every queue maintenance action must bind to exactly one queued item.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Try adjacent page, index, or origin values and assert only the intended item changes.

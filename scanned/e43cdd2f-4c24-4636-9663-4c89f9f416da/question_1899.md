# Q1899: reap_page can confuse page, index, or origin binding

## Question
Can an unprivileged attacker use `reap_page` with crafted call repetition, batching order, and surrounding state so the runtime operates on the wrong page, index, or message origin?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::reap_page
- Entrypoint: public message maintenance extrinsic `reap_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe aliasing and boundary checks for page, index, and origin identifiers.
- Invariant to test: Every queue maintenance action must bind to exactly one queued item.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Try adjacent page, index, or origin values and assert only the intended item changes.

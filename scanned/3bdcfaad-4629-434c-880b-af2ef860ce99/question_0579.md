# Q0579: reap_page can delete live queue state too early

## Question
Can an unprivileged attacker use `reap_page` to reap, settle, or bypass queue state before all dependent work is truly complete?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::reap_page
- Entrypoint: public message maintenance extrinsic `reap_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Target cleanup logic that trusts a derived marker more than the underlying execution record.
- Invariant to test: Queue cleanup must require a terminal state agreed by every related marker.
- Expected Immunefi impact: Permanent message stall or block-production degradation
- Fast validation: Drive messages to partially complete states and attempt cleanup at each boundary.

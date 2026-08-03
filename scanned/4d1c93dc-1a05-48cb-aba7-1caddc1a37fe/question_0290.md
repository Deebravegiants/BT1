# Q0290: reap_page can replay a message or execution slot

## Question
Can an unprivileged attacker use `reap_page` to execute or settle the same message, page entry, or delivery slot more than once?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::reap_page
- Entrypoint: public message maintenance extrinsic `reap_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for stale markers or alternate public paths that consume the same unit of work under different keys.
- Invariant to test: Each queued message or receipt must be processed exactly once.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Execute or settle one unit once, then probe every public path that could still reference it.

# Q0289: execute_overweight can replay a message or execution slot

## Question
Can an unprivileged attacker use `execute_overweight` to execute or settle the same message, page entry, or delivery slot more than once?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::execute_overweight
- Entrypoint: public message maintenance extrinsic `execute_overweight`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for stale markers or alternate public paths that consume the same unit of work under different keys.
- Invariant to test: Each queued message or receipt must be processed exactly once.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Execute or settle one unit once, then probe every public path that could still reference it.

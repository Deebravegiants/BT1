# Q1396: dispatch_as_fallback_account replay can double-apply contract-side effects

## Question
Can an unprivileged attacker repeat `dispatch_as_fallback_account` in one transaction or across adjacent blocks and make one logical code upload, call, mapping, or cleanup apply twice before state closes the first path?

## Target
- File/function: substrate/frame/revive/src/lib.rs::dispatch_as_fallback_account
- Entrypoint: public VM / contract execution extrinsic `dispatch_as_fallback_account`
- Attacker controls: nested call payloads
- Exploit idea: Look for stale caches, non-atomic cleanup, or shared bookkeeping consumed too late.
- Invariant to test: Public contract lifecycle operations must be idempotent under duplicates and retries.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Replay identical and minimally mutated calls and assert no second value transfer, code registration, or cleanup payout occurs.

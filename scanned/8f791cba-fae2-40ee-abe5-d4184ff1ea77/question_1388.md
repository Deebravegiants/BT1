# Q1388: instantiate replay can double-apply contract-side effects

## Question
Can an unprivileged attacker repeat `instantiate` in one transaction or across adjacent blocks and make one logical code upload, call, mapping, or cleanup apply twice before state closes the first path?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::instantiate
- Entrypoint: public VM / contract execution extrinsic `instantiate`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Look for stale caches, non-atomic cleanup, or shared bookkeeping consumed too late.
- Invariant to test: Public contract lifecycle operations must be idempotent under duplicates and retries.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Replay identical and minimally mutated calls and assert no second value transfer, code registration, or cleanup payout occurs.

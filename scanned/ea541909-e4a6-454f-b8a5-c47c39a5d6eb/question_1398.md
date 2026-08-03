# Q1398: eth_instantiate_with_code replay can double-apply contract-side effects

## Question
Can an unprivileged attacker repeat `eth_instantiate_with_code` in one transaction or across adjacent blocks and make one logical code upload, call, mapping, or cleanup apply twice before state closes the first path?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_instantiate_with_code
- Entrypoint: public VM / contract execution extrinsic `eth_instantiate_with_code`
- Attacker controls: amounts, fees, or prices, duplicate or adversarial list ordering
- Exploit idea: Look for stale caches, non-atomic cleanup, or shared bookkeeping consumed too late.
- Invariant to test: Public contract lifecycle operations must be idempotent under duplicates and retries.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Replay identical and minimally mutated calls and assert no second value transfer, code registration, or cleanup payout occurs.

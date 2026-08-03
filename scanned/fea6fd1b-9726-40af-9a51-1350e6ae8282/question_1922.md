# Q1922: eth_substrate_call can create persistent public VM griefing

## Question
Can an unprivileged attacker use `eth_substrate_call` to keep the runtime doing underpriced heavy VM or host work repeatedly enough to degrade block production?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_substrate_call
- Entrypoint: public VM / contract execution extrinsic `eth_substrate_call`
- Attacker controls: nested call payloads, duplicate or adversarial list ordering
- Exploit idea: Search for public execution shapes that maximize real work per charged unit or preserve expensive cleanup for later blocks.
- Invariant to test: Worst-case public VM work must remain within charged weight and must not create a repeatable block-slowdown path.
- Expected Immunefi impact: Chain halt / block-production slowdown from undercharged VM execution
- Fast validation: Fuzz maximal code size, call depth, revert depth, storage growth, and repeated cleanup patterns.

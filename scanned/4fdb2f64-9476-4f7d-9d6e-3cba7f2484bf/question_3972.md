# Q3972: eth_substrate_call can bind outer metadata more weakly than inner payload

## Question
Can an unprivileged attacker keep the inner payload accepted by `eth_substrate_call` constant while mutating outer metadata such as declared length, count, route, or wrapper context and obtain a different economic result?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_substrate_call
- Entrypoint: public VM / contract execution extrinsic `eth_substrate_call`
- Attacker controls: nested call payloads, duplicate or adversarial list ordering
- Exploit idea: Focus on mismatches between what the outer envelope claims and what the verified inner payload actually authorizes.
- Invariant to test: Outer metadata must not change the semantic effect of an already-verified inner payload except in explicitly validated ways.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Replay the same inner payload under alternate outer envelopes and compare charging, routing, and settlement outcomes.

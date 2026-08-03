# Q3969: dispatch_as_fallback_account can bind outer metadata more weakly than inner payload

## Question
Can an unprivileged attacker keep the inner payload accepted by `dispatch_as_fallback_account` constant while mutating outer metadata such as declared length, count, route, or wrapper context and obtain a different economic result?

## Target
- File/function: substrate/frame/revive/src/lib.rs::dispatch_as_fallback_account
- Entrypoint: public VM / contract execution extrinsic `dispatch_as_fallback_account`
- Attacker controls: nested call payloads
- Exploit idea: Focus on mismatches between what the outer envelope claims and what the verified inner payload actually authorizes.
- Invariant to test: Outer metadata must not change the semantic effect of an already-verified inner payload except in explicitly validated ways.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Replay the same inner payload under alternate outer envelopes and compare charging, routing, and settlement outcomes.

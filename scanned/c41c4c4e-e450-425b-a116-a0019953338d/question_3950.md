# Q3950: submit_commitment can bind outer metadata more weakly than inner payload

## Question
Can an unprivileged attacker keep the inner payload accepted by `submit_commitment` constant while mutating outer metadata such as declared length, count, route, or wrapper context and obtain a different economic result?

## Target
- File/function: bridges/modules/beefy/src/lib.rs::submit_commitment
- Entrypoint: public proof / message submission extrinsic `submit_commitment`
- Attacker controls: proof or signed payload contents
- Exploit idea: Focus on mismatches between what the outer envelope claims and what the verified inner payload actually authorizes.
- Invariant to test: Outer metadata must not change the semantic effect of an already-verified inner payload except in explicitly validated ways.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Replay the same inner payload under alternate outer envelopes and compare charging, routing, and settlement outcomes.

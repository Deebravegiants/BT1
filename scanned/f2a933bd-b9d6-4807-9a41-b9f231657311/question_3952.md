# Q3952: submit_finality_proof_ex can bind outer metadata more weakly than inner payload

## Question
Can an unprivileged attacker keep the inner payload accepted by `submit_finality_proof_ex` constant while mutating outer metadata such as declared length, count, route, or wrapper context and obtain a different economic result?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof_ex
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof_ex`
- Attacker controls: proof or signed payload contents
- Exploit idea: Focus on mismatches between what the outer envelope claims and what the verified inner payload actually authorizes.
- Invariant to test: Outer metadata must not change the semantic effect of an already-verified inner payload except in explicitly validated ways.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Replay the same inner payload under alternate outer envelopes and compare charging, routing, and settlement outcomes.

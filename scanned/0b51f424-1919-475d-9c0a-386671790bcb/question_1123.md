# Q1123: submit_finality_proof can mis-bind lane, channel, or origin context

## Question
Can an unprivileged attacker call `submit_finality_proof` with crafted proof or signed payload contents so a valid proof or message for one lane, channel, parachain, or origin is applied to another?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Probe whether route-identifying metadata is fully bound into verification and settlement.
- Invariant to test: Every bridged message or proof must bind to exactly one route and one origin domain.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Reuse a valid proof across adjacent lanes, channels, or origins and assert every mismatch is rejected.

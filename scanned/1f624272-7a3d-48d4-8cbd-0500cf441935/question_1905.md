# Q1905: submit_parachain_heads can confuse route, authority, or receipt transitions

## Question
Can an unprivileged attacker use `submit_parachain_heads` at a boundary where routes, authority sets, receipts, or retained heads roll over and make the bridge accept a transition it should reject?

## Target
- File/function: bridges/modules/parachains/src/lib.rs::submit_parachain_heads
- Entrypoint: public proof / message submission extrinsic `submit_parachain_heads`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Probe the exact rollover or pruning boundary where one validated object both advances state and changes the rules for the next one.
- Invariant to test: Boundary transitions must be atomic, monotonic, and justified by exactly the required validated data.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Submit objects immediately before, at, and after rollover boundaries and diff state progression.

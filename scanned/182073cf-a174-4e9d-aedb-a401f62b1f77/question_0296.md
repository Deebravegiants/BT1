# Q0296: submit_parachain_heads can undercharge proof verification

## Question
Can an unprivileged attacker use `submit_parachain_heads` with crafted proof or signed payload contents, duplicate or adversarial list ordering so the call pays for less verification or dispatch work than it actually triggers?

## Target
- File/function: bridges/modules/parachains/src/lib.rs::submit_parachain_heads
- Entrypoint: public proof / message submission extrinsic `submit_parachain_heads`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Probe declared counts, weights, vector sizes, and payload sizes against real proof complexity.
- Invariant to test: Worst-case verification and dispatch work must remain within charged weight.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Fuzz maximal proof sizes, message counts, header ancestries, and dispatch weight declarations.

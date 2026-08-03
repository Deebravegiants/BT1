# Q0293: submit_finality_proof_ex can undercharge proof verification

## Question
Can an unprivileged attacker use `submit_finality_proof_ex` with crafted proof or signed payload contents so the call pays for less verification or dispatch work than it actually triggers?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof_ex
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof_ex`
- Attacker controls: proof or signed payload contents
- Exploit idea: Probe declared counts, weights, vector sizes, and payload sizes against real proof complexity.
- Invariant to test: Worst-case verification and dispatch work must remain within charged weight.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Fuzz maximal proof sizes, message counts, header ancestries, and dispatch weight declarations.

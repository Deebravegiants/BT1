# Q2613: submit_finality_proof can write state that another public path misreads

## Question
Can an unprivileged attacker use `submit_finality_proof` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

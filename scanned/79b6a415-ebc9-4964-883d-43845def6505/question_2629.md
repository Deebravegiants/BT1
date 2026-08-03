# Q2629: dispatch can write state that another public path misreads

## Question
Can an unprivileged attacker use `dispatch` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/meta-tx/src/lib.rs::dispatch
- Entrypoint: public dispatch wrapper `dispatch`
- Attacker controls: proof or signed payload contents, nested call payloads, batched or wrapped execution context
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

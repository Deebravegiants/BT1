# Q2824: second can write state that another public path misreads

## Question
Can an unprivileged attacker use `second` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/democracy/src/lib.rs::second
- Entrypoint: signed extrinsic `second`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

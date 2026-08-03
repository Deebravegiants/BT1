# Q2715: set_commission_claim_permission can write state that another public path misreads

## Question
Can an unprivileged attacker use `set_commission_claim_permission` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::set_commission_claim_permission
- Entrypoint: signed extrinsic `set_commission_claim_permission`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

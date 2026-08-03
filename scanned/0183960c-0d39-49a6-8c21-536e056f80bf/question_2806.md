# Q2806: delete_collection can write state that another public path misreads

## Question
Can an unprivileged attacker use `delete_collection` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::delete_collection
- Entrypoint: signed extrinsic `delete_collection`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

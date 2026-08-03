# Q2814: thaw_collection can write state that another public path misreads

## Question
Can an unprivileged attacker use `thaw_collection` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::thaw_collection
- Entrypoint: signed extrinsic `thaw_collection`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

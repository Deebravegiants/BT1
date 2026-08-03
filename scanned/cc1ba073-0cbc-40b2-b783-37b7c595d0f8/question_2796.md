# Q2796: set_attribute can write state that another public path misreads

## Question
Can an unprivileged attacker use `set_attribute` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_attribute
- Entrypoint: signed extrinsic `set_attribute`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.

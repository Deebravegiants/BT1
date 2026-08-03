# Q1333: set_metadata can mishandle deposits or storage refunds

## Question
Can an unprivileged attacker use `set_metadata` to free a deposit, attribute deposit, or metadata deposit without actually removing the underlying state, or remove state without releasing the deposit?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_metadata
- Entrypoint: signed extrinsic `set_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Look for lifecycle paths where deposit ownership and stored object cleanup are updated in separate steps.
- Invariant to test: Deposits and the state they fund must be one-to-one across create, mutate, transfer, and destroy paths.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Track every deposit-bearing field through creation, mutation, transfer, and destruction.

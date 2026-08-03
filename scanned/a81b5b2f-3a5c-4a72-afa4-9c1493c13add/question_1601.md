# Q1601: delete_collection can settle against stale sale or swap witnesses

## Question
Can an unprivileged attacker reach `delete_collection` with stale price, deadline, desired-item, or witness data and still settle on favorable terms?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::delete_collection
- Entrypoint: signed extrinsic `delete_collection`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Exercise expired, canceled, or already-consumed sale or swap state with minimally changed parameters.
- Invariant to test: Public settlement must consume exactly the still-live sale or swap state and nothing older.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Cancel or fulfill a sale or swap, then attempt settlement again with stale witnesses and equivalent item IDs.

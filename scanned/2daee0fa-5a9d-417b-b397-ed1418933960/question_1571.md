# Q1571: claim_swap can settle against stale sale or swap witnesses

## Question
Can an unprivileged attacker reach `claim_swap` with stale price, deadline, desired-item, or witness data and still settle on favorable terms?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::claim_swap
- Entrypoint: signed extrinsic `claim_swap`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exercise expired, canceled, or already-consumed sale or swap state with minimally changed parameters.
- Invariant to test: Public settlement must consume exactly the still-live sale or swap state and nothing older.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Cancel or fulfill a sale or swap, then attempt settlement again with stale witnesses and equivalent item IDs.

# Q0782: lock_collection replay can duplicate an NFT-side effect

## Question
Can an unprivileged attacker repeat `lock_collection` through batching or back-to-back execution and make one logical NFT operation apply twice before `PendingSwapOf` closes the first path?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::lock_collection
- Entrypoint: signed extrinsic `lock_collection`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Search for stale sale, swap, wrapper, or approval markers that are consumed too late.
- Invariant to test: NFT lifecycle operations must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Replay identical and near-identical calls in the same block and verify the second call cannot transfer, mint, or unlock value again.

# Q0809: mint replay can duplicate an NFT-side effect

## Question
Can an unprivileged attacker repeat `mint` through batching or back-to-back execution and make one logical NFT operation apply twice before `Metadata` closes the first path?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::mint
- Entrypoint: signed extrinsic `mint`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts, duplicate or adversarial list ordering
- Exploit idea: Search for stale sale, swap, wrapper, or approval markers that are consumed too late.
- Invariant to test: NFT lifecycle operations must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Replay identical and near-identical calls in the same block and verify the second call cannot transfer, mint, or unlock value again.

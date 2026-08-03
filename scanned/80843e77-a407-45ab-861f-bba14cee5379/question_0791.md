# Q0791: set_attributes_pre_signed replay can duplicate an NFT-side effect

## Question
Can an unprivileged attacker repeat `set_attributes_pre_signed` through batching or back-to-back execution and make one logical NFT operation apply twice before `PendingSwapOf` closes the first path?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_attributes_pre_signed
- Entrypoint: signed extrinsic `set_attributes_pre_signed`
- Attacker controls: proof or signed payload contents, beneficiary, delegate, or target accounts
- Exploit idea: Search for stale sale, swap, wrapper, or approval markers that are consumed too late.
- Invariant to test: NFT lifecycle operations must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Replay identical and near-identical calls in the same block and verify the second call cannot transfer, mint, or unlock value again.

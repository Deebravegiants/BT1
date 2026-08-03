# Q0819: clear_attribute replay can duplicate an NFT-side effect

## Question
Can an unprivileged attacker repeat `clear_attribute` through batching or back-to-back execution and make one logical NFT operation apply twice before `Approvals` closes the first path?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::clear_attribute
- Entrypoint: signed extrinsic `clear_attribute`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Search for stale sale, swap, wrapper, or approval markers that are consumed too late.
- Invariant to test: NFT lifecycle operations must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Replay identical and near-identical calls in the same block and verify the second call cannot transfer, mint, or unlock value again.

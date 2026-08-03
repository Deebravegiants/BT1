# Q0808: force_transfer replay can duplicate an NFT-side effect

## Question
Can an unprivileged attacker repeat `force_transfer` through batching or back-to-back execution and make one logical NFT operation apply twice before `Metadata` closes the first path?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::force_transfer
- Entrypoint: signed extrinsic `force_transfer`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Search for stale sale, swap, wrapper, or approval markers that are consumed too late.
- Invariant to test: NFT lifecycle operations must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Replay identical and near-identical calls in the same block and verify the second call cannot transfer, mint, or unlock value again.

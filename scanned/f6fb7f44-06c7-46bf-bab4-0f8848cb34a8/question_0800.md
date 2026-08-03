# Q0800: update_mint_settings replay can duplicate an NFT-side effect

## Question
Can an unprivileged attacker repeat `update_mint_settings` through batching or back-to-back execution and make one logical NFT operation apply twice before `PendingSwapOf` closes the first path?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::update_mint_settings
- Entrypoint: signed extrinsic `update_mint_settings`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Search for stale sale, swap, wrapper, or approval markers that are consumed too late.
- Invariant to test: NFT lifecycle operations must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Replay identical and near-identical calls in the same block and verify the second call cannot transfer, mint, or unlock value again.

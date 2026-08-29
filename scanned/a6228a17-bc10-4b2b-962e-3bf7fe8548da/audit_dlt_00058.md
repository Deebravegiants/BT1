# [M] Sync restart poisoning from single unauthenticated peer via above-lookahead block

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52737
CWE: Insufficient Verification of Data Authenticity
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-gvjc-3w7c-92jx
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node accepts inbound P2P connections and is syncing or catching up to the chain tip.

### Summary

A malicious peer can answer Zebra's outbound `getblocks`/`FindBlocks` request with a small two-hash inventory, then serve a syntactically valid block whose coinbase height is far above the victim's local tip. The `AboveLookaheadHeightLimit` error in the sync download pipeline triggers a global sync restart rather than being scoped to the offending peer. The peer is never scored or disconnected because the error type does not carry the advertiser address.

On mainnet, each successful cycle imposes a 67-second sync restart delay. All in-flight downloads from honest peers are cancelled on each restart.

### Details

The bug is the interaction of three layers:

1. The syncer promotes unvalidated `FindBlocks` peer responses into concrete download schedules without checking that the advertised hashes are plausible chain extensions.

2. When a downloaded block's coinbase height exceeds `tip + VERIFICATION_PIPELINE_DROP_LIMIT`, the sync downloader returns `BlockDownloadVerifyError::AboveLookaheadHeightLimit`. This error variant carries only the block height and hash, not the advertiser peer address.

3. The sync error handler in `handle_block_response` only sends misbehaviour scores for `BlockDownloadVerifyError::Invalid` errors that carry an `advertiser_addr` and have a nonzero `misbehavior_score()`. `AboveLookaheadHeightLimit` falls through to the default restart-worthy path, cancelling all in-flight downloads and waiting 67 seconds before restarting sync.

The attacker needs only an unauthenticated P2P connection (post-handshake), a tiny payload (one two-hash `inv` message plus one small block per cycle), and no mining capability, funds, or valid chain data. The peer is never penalised, so the attack is repeatable indefinitely.

Additionally, several other pre-consensus sync-layer errors had zero misbehaviour scores even when peer-attributed. Contextual validation failures (`InvalidDifficultyThreshold`, `TimeTooEarly`, `TimeTooLate`, `NonSequentialBlock`) and locktime failures from block-serving peers all scored zero, allowing repeated abuse without penalty.

### Patches

Patched in Zebra 4.4.2. The fix:

- Carries `advertiser_addr` through `AboveLookaheadHeightLimit` and `InvalidHeight` error variants.
- Makes above-lookahead and invalid-height failures peer-local (the block is dropped and the peer is banned with score 100) rather than triggering a global sync restart.
- Expands `misbehavior_score()` across `BlockError`, `VerifyBlockError`, and `CommitBlockError` to cover contextual validation failures that previously scored zero.

### Workarounds

No configuration-level workaround is available. The attack is mitigated by having a diverse honest peer set, but cannot be prevented while the vulnerable code is running.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-gvjc-3w7c-92jx_

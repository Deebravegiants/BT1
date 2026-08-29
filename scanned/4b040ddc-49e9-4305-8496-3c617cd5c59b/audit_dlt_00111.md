# [H] Pacaya inbox verification pointer corruption

## Summary
Severity: High
Chain: Taiko
Component: taikoxyz/taiko-mono
CVE: CVE-2025-66559
Published: 2025-12-04
Source: https://github.com/taikoxyz/taiko-mono/security/advisories/GHSA-5mxh-r33p-6h5x
Type: github-advisory

## Details
`TaikoInbox._verifyBatches` (packages/protocol/contracts/layer1/based/TaikoInbox.sol:627-678) advanced the local `tid` to whatever transition matched the current `blockHash` before knowing whether that batch would actually be verified. When the loop later broke (e.g., cooldown window not yet passed or transition invalidated), the function still wrote that newer `tid` into `batches[lastVerifiedBatchId].verifiedTransitionId` after decrementing `batchId`. Result: the last verified batch could end up pointing at a transition index from the *next* batch (often zeroed), corrupting the verified chain pointer.

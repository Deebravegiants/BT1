# [M] M-4 nextCollectionId should be limited

## Summary
Severity: Medium
Contest weight: 0.0391
Dataset id: 8006
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains an unchecked growth of the internal counter that tracks the next collection identifier (nextCollectionId). Because the claiming function performs a validation that assumes collection identifiers are below a certain threshold, the absence of an explicit upper‑bound check allows nextCollectionId to increase without limit. When the identifier reaches or exceeds 100 000, the token‑id verification logic in the claim path triggers a revert, preventing any further claims for those collections. This situation arises after enough collections have been created, either through normal usage or by an adversary deliberately inflating the counter. Users attempting to claim NFTs from a high‑id collection experience a failed transaction and receive no tokens, effectively losing access to their expected assets. The protocol’s accounting assumptions – that every collection can be claimed – are violated, leading to a denial‑of‑service condition for affected collections and potentially locking any funds attached to the claim process. The issue was identified during a systematic audit that examined the claim routine and noticed the reliance on a hard‑coded range without a protective guard. It can be difficult to spot in testing because typical deployments never reach such high identifiers, so the bug remains dormant until the counter grows large enough. The recommended remediation is to enforce a maximum value for nextCollectionId (for example, require nextCollectionId < 1 000 000) before allowing collection creation or increment, thereby ensuring the claim logic always operates within its expected numeric bounds.

## Recommendation
We recommend adding the following check: nextCollectionId < 1000000.

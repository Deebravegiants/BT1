# [M] M-7 Modifier onlyValidCollectionId() is missing

## Summary
Severity: Medium
Contest weight: 0.0177
Dataset id: 8010
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing validation step in a function that handles collection identifiers. The contract is supposed to restrict operations to existing, authorized collections by applying the onlyValidCollectionId() modifier, but the modifier is absent at the indicated lines. As a result, the function accepts any uint256 value supplied as a collection identifier without checking whether the identifier corresponds to a registered collection or whether the caller has permission to act on it. This omission creates an input‑validation flaw that can be exploited by an attacker who supplies an arbitrary or non‑existent collection ID. By doing so, the attacker can trigger minting, transfer, or accounting logic that assumes the collection is valid, leading to the creation of NFTs in unintended collections, misallocation of funds, or failure of downstream accounting such as refunds or balance updates. From a user’s perspective the symptoms may include receiving an NFT that appears under the wrong collection, seeing a refund amount of zero, or observing that a balance that should have increased remains unchanged. The issue manifests whenever the vulnerable function is called, regardless of the caller’s role, because there is no guard enforcing collection existence. The problem was discovered during a systematic security audit performed by MixBytes, which flagged the missing onlyValidCollectionId() modifier as a medium‑severity risk. Because the function still executes and does not revert, the bug can be subtle and may only become apparent when downstream operations fail or when users notice unexpected token behavior. The root cause is an omitted access‑control / input‑validation check, a common class of bug where a contract fails to enforce business‑logic constraints on critical parameters. To remediate the issue, the contract should be updated to include the onlyValidCollectionId() modifier (or an equivalent explicit require statement) on the affected function, ensuring that only registered collection identifiers are accepted and that any attempt to use an invalid ID results in a revert, thereby preserving the integrity of the protocol’s accounting and user expectations.

## Recommendation
We recommend adding the onlyValidCollectionId() modifier.

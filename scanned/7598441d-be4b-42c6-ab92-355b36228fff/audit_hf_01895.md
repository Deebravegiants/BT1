# [C] NFTs can be stolen by calling send() and receiving the nfts in another chain

## Summary
Severity: Critical
Contest weight: 0.0356
Dataset id: 10475
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an authorization bypass in the NFT transfer routine named send(). The routine is intended to move NFTs from the current chain to another chain, but it fails to verify that the caller is either the owner of the token or an approved operator. Because the function does not invoke the standard _isApprovedOrOwner check, any address can invoke send() with an arbitrary token identifier. An attacker can therefore call send() with a tokenId that belongs to an unsuspecting user, causing the contract to lock the token on the source chain and mint or release a corresponding NFT on the destination chain that is credited to the attacker. This results in the original holder losing possession of the NFT, often seeing their balance drop to zero in the UI, while the attacker receives the asset on the other chain. The flaw occurs whenever the send() function is executed; there is no conditional guard based on token ownership, so the exploit works under normal transaction conditions without requiring any special state. All NFT owners, collectors, and any participants relying on the cross‑chain bridge are affected because their assets can be taken without consent. The issue was discovered during a manual audit that compared the send() implementation against the ERC‑721 access‑control expectations. It can be hard to notice because the function may appear to perform a legitimate bridging operation, and the missing check does not generate an explicit error; the token simply disappears from the source chain. Conceptually, the bug belongs to the class of missing access‑control checks or authorization bypasses, similar to “anyone can transfer without approval” flaws. To remediate, the send() routine should enforce the same ownership or approval verification used by standard ERC‑721 transfer functions, typically by calling _isApprovedOrOwner(msg.sender, tokenId) before proceeding with the cross‑chain operation. This restores the invariant that only the rightful owner or an authorized operator can initiate a transfer, preventing unauthorized stealing of NFTs and preserving the accounting guarantees of the protocol.

## Recommendation
Add _isApprovedOrOwner() on the nfts to be sent in send().

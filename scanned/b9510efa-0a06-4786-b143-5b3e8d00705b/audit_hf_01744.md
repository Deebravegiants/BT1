# [M] M-4 There is no recovery option for ERC721

## Summary
Severity: Medium
Contest weight: 0.0168
Dataset id: 9532
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue is a missing recovery mechanism for ERC721 (non‑fungible) tokens in the Lido contract. The transferToVault() function is designed to move assets to a vault but only implements logic for ERC20‑style tokens, ignoring the ERC721 interface that requires a tokenId and safeTransferFrom call. Because the contract does not implement ERC721Receiver or provide a withdraw function for NFTs, any ERC721 token that is accidentally or intentionally sent to the contract becomes permanently locked. This situation arises whenever a user or a malicious actor transfers an NFT to the Lido contract address, either directly or via a generic token‑transfer call that the contract does not reject. From the user’s perspective the symptom is that the NFT disappears from their wallet, the UI shows no balance for that token, and attempts to retrieve it return nothing. The root cause is the absence of code handling the ERC721 transfer hook and the lack of an administrative function that can call safeTransferFrom to return the token. The vulnerability was identified during a manual audit of the contract’s token‑handling functions. It can be hard to notice because the contract compiles and works correctly for supported token standards, and no tests exercised ERC721 paths. The impact is that users may lose ownership of valuable NFTs, which undermines trust in the protocol and may expose the project to reputational damage. To remediate, the contract should be extended to implement the ERC721Receiver interface, add a function (restricted to an authorized role) that can call safeTransferFrom with a specific tokenId to move the NFT out of the contract, and optionally emit events to track recovery actions. This aligns the recovery logic with the ERC721 standard and ensures that NFTs are not permanently trapped.

## Recommendation
It is necessary to add another function to recover ERC721.

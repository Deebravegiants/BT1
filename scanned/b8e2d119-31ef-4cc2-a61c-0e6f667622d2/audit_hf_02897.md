# [H] 721A-1 | Wrong Token Sent

## Summary
Severity: High
Contest weight: 0.0471
Dataset id: 16198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an off‑by‑one error in the token transfer logic of an ERC721A‑style contract. The function that is supposed to hand over a specific NFT first validates that the supplied tokenId belongs to the caller by checking that the tokenId maps to msg.sender. After this verification the contract mistakenly calls the internal transfer routine with tokenId+1 instead of the verified tokenId. Because the check and the actual transfer use different identifiers, the contract can send a token that the caller does not own, or even a token that has not been minted yet. This mismatch can be exploited by a malicious actor who triggers the function expecting to receive a known token but receives the next token in the sequence, potentially allowing the attacker to acquire an NFT without proper authorization or to cause the intended token to become locked in an inconsistent state. The impact includes loss of ownership for honest users, unexpected changes in token balances, and a breach of the protocol’s accounting assumptions that each token is uniquely tied to its owner. The bug manifests whenever the vulnerable function is invoked – typically during a claim, withdrawal, or mint‑to‑user operation – because the condition that checks ownership is satisfied but the subsequent transfer uses the wrong identifier. All token holders and any downstream logic that relies on correct token ownership are affected. The issue was discovered during a manual audit by the Guardian team, who noticed that the verification step referenced tokenId while the transfer step referenced tokenId+1. The problem is subtle because the transferred token may still be a valid token, so the UI may simply show a different token ID without obvious error messages, making it hard for users to notice that they received the wrong asset. To remediate the issue, the contract should be updated to pass the verified tokenId to the transfer routine, ensuring that the token that was checked against the caller’s address is the one actually transferred. This aligns the verification and execution paths and restores the intended one‑to‑one relationship between a user and their NFT, eliminating the risk of unintended token movement and preserving the integrity of the platform’s accounting model.

## Recommendation
Send the current tokenId to msg.sender.

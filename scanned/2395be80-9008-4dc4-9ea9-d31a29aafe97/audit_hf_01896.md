# [C] deTokenize() is missing access control, anyone can burn other people's nfts

## Summary
Severity: Critical
Contest weight: 0.0353
Dataset id: 10476
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unauthorized token burn caused by missing access control in the deTokenize() function. The function is intended to let a token holder destroy (burn) their own NFT by providing a URL, but it does not verify that the caller is the token owner or an approved operator. Because the function is public and lacks the onlyOwner modifier or a call to _isApprovedOrOwner(), any address can invoke it with an arbitrary token identifier. An attacker can therefore submit a deTokenize transaction specifying a victim’s tokenId, causing the contract to call the internal burn routine and permanently remove the NFT from the victim’s balance. This results in the loss of the unique asset, potential loss of associated value, and a breach of the protocol’s accounting assumptions that only owners may destroy their tokens. The issue manifests whenever deTokenize is called, regardless of who initiates the transaction, and it affects all token holders, the protocol’s supply metrics, and any downstream applications that rely on NFT ownership. The flaw was discovered during a manual audit that reviewed function visibility and access patterns; the missing check is easy to overlook because the function name suggests a benign operation and the code does not emit explicit warnings. From a user’s perspective the symptom is that an NFT they owned suddenly disappears from their wallet, with no transaction from their address, leading to confusion and loss of trust. The bug belongs to the class of “missing authorization” or “access‑control bypass” vulnerabilities, where a privileged operation is exposed without proper permission checks. To remediate, the function should be restricted either by applying the onlyOwner modifier (if only the contract owner may burn) or, more appropriately, by invoking the standard ERC‑721 authorization helper _isApprovedOrOwner() to ensure that only the token’s owner or an approved operator can trigger the burn. Adding this check restores the intended business logic that only rightful owners may destroy their assets and prevents arbitrary destruction of third‑party NFTs.

## Recommendation
Either place the onlyOwner modifier or call _isApprovedOrOwner().

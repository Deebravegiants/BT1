# [H] `_transferNFTs

## Summary
Severity: High
Contest weight: 0.2217
Dataset id: 11764
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an NFT is sold that does not specify support for the ERC-721 or ERC-1155 standard interface, the sale will still succeed. In doing so, the seller will receive funds from the buyer, but the buyer will not receive any NFT from the seller. This could happen in the following cases:

1. A token that claims to be ERC-721/1155 compliant, but fails to implement the `supportsInterface()` function properly.
2. An NFT that follows a standard other than ERC-721/1155 and does not implement their EIP-165 interfaces.
3. A malicious contract that is deployed to take advantage of this behavior.

## Proof of Concept
<https://gist.github.com/kylriley/3bf0e03d79b3d62dd5a9224ca00c4cb9>

## Recommendation
If neither the ERC-721 nor the ERC-1155 interface is supported the function should revert. An alternative approach would be to attempt a `transferFrom` and check the balance before and after to ensure that it succeeded.

Fixed in <https://github.com/infinitydotxyz/exchange-contracts-v2/commit/377c77f0888fea9ca1e087de701b5384a046f760>

If `supportsInterface` returns false for both 721 & 1155 then no NFT is transferred but funds are still sent to the seller.

A number of NFTs do not fully comply with the 721/1155 standards. Since the order is not canceled or the tx reverted, this seems like a High risk issue.

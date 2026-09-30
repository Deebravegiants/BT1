# [M] Lack of replay protection for mintAllowList and mintSigned

## Summary
Severity: Medium
Contest weight: 0.1826
Dataset id: 14920
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case of mintSigned (minting via signatures) and mintAllowList (minting via merkle proofs) there are no checks that prevent re-using the same signature or Merkle proof multiple times. This is indirectly enforced by the _checkMintQuantity function that checks the mint statistics using IERC721SeaDrop(nftContract).getMintStats(minter) and reverting if the quantity exceeds maxMintsPerWallet. Replays can happen if a wallet does not claim all of maxMintsPerWallet in one transaction. For example, assume that maxMintsPerWallet is set to 2. A user can call mintSigned with a valid signature and quantity = 1 twice. Typically, contracts try to avoid any forms of signature replays, i.e., a signature can only be used once. This simplifies the security properties. In the current implementation of the ERC721Seadrop contract, we couldn't see a way to exploit replay protection to mint beyond what could be minted in a single initial transaction with the maximum value of quantity supplied. However, this relies on the contract correctly implementing IERC721SeaDrop.getMintStats.

## Recommendation
We recommend implementing replay protection for both cases. Here are some ideas to do this:
1. Consider also including the tokenId for the signature and passing that along in mintSeaDrop call. This way, even if the signature is replayed, minting the same tokenId should not be possible--most ERC-721 libraries prevent this. However, some care should be made to check the following case: mint a fixed token id using the signature, then burn the token id, and resurrecting the same token id by replaying the signature.
2. Consider storing the digest and if a digest is used once, then it shouldn't be able to use again.
3. Do not use signature as a way to check if something was consumed. They are malleable.

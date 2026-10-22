# [M] There is no Support For The Trading of Cryptopunks

## Summary
Severity: Medium
Contest weight: 0.1475
Dataset id: 1600
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Cryptopunks are at the core of the NFT ecosystem. As one of the first NFTs, it embodies the culture of NFT marketplaces. By not supporting the trading of cryptopunks, Foundation is at a severe disadvantage when compared to other marketplaces. Cryptopunks have their own internal marketplace which allows users to trade their NFTs to other users. As such, cryptopunks does not adhere to the `ERC721` standard, it will always fail when the protocol attempts to trade them.

## Proof of Concept
Here is an example [implementation](https://github.com/code-423n4/2021-12-nftx/blob/main/nftx-protocol-v2/contracts/solidity/NFTXStakingZap.sol#L417-L424) of what it might look like to integrate cryptopunks into the Foundation protocol.

## Recommendation
Consider designing a wrapper contract for cryptopunks to facilitate standard `ERC721` transfers. The logic should be abstracted away from the user such that their user experience is not impacted.
Yes, crypto punks is an important part of the ecosystem and this is on our radar. We are not planning on adding support at this time but we will revisiting this in the future.

I like the idea of using a wrapper contract of sorts. We will be looking for a way to keep the complexity out of the market contract itself like you suggest if at all possible.

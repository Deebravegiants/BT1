# [M] There is no Support For The Trading of Cryptopunks

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-foundation
Published: 2022-03-02
Source: https://github.com/code-423n4/2022-02-foundation-findings/issues/74
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-foundation/tree/main/contracts


# Vulnerability details

## Impact

Cryptopunks are at the core of the NFT ecosystem. As one of the first NFTs, it embodies the culture of NFT marketplaces. By not supporting the trading of cryptopunks, Foundation is at a severe disadvantage when compared to other marketplaces. Cryptopunks have their own internal marketplace which allows users to trade their NFTs to other users. As such, cryptopunks does not adhere to the `ERC721` standard, it will always fail when the protocol attempts to trade them.

## Proof of Concept

Here is an example [implementation](https://github.com/code-423n4/2021-12-nftx/blob/main/nftx-protocol-v2/contracts/solidity/NFTXStakingZap.sol#L417-L424) of what it might look like to integrate cryptopunks into the Foundation protocol.

## Tools Used

Manual code review.

## Recommended Mitigation Steps

Consider designing a wrapper contract for cryptopunks to facilitate standard `ERC721` transfers. The logic should be abstracted away from the user such that their user experience is not impacted.

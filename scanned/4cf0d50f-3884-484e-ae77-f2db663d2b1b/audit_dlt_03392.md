# [M] NFTs initially of similar price may change significantly in value leading to unfair ownership changes

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-11
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/74
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Vaults might start off as holding NFTs of similar price but over time some of them might be revealed as having unique/hidden features (or older ones with lower IDs) leading to increased demand (e.g. certain Hashmasks or Cryptopunks) which might significantly increase their value compared to others in the vault. The protocol specification/design treats all of them as the same allowing a user to redeem potentially higher-valued NFT(s) (using directRedeem/swap) later having minted lower-valued one(s) earlier.

The impact could be significant to users based on the value of the NFTs minted/redeemed. Owners of NFTs whose value increases significantly at a later time may lose “ownership" of their earlier minted ones to someone else who specifically redeems their NFTs anticipating/knowing the increased valuation. This leads to perceived ownership/value loss.

## Proof of Concept


https://github.com/code-423n4/2021-05-nftx/blob/f6d793c136d110774de259d9f3b25d003c4f8098/nftx-protocol-v2/contracts/solidity/NFTXVaultUpgradeable.sol#L207-L223


https://github.com/code-423n4/2021-05-nftx/blob/f6d793c136d110774de259d9f3b25d003c4f8098/nftx-protocol-v2/contracts/solidity/NFTXVaultUpgradeable.sol#L233-L257


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Given that this indexing is fundamental to the protocol offering, design and assumptions, not sure if there is a specific mitigation. Removing the ability to directRedeem could perhaps make redeeming entirely pseudo-random to everyone and seemingly more fair.

# [M] NFT owner can change tokenURI

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-skale
Published: 2022-02-25
Source: https://github.com/code-423n4/2022-02-skale-findings/issues/26
Type: code-finding

## Details
# Lines of code

https://github.com/skalenetwork/ima-c4-audit/blob/11d6a6ae5bf16af552edd75183791375e501915f/contracts/schain/tokens/ERC721OnChain.sol#L73


# Vulnerability details

## Impact
In the `ERC721OnChain` implementation the _token owner_ can set the token's URI using `setTokenURI`.
Usually, this is token URI points to data defining the NFT (attributes, images, etc.).
It's usually set by the _contract_ owner.
A user that owns an NFT can just spoof any other NFT data by changing the token URI to any of the other NFTs.

## Recommended Mitigation Steps
Disallow the owner of an NFT to change its token URI

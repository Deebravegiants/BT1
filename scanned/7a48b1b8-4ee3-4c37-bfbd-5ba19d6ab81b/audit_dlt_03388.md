# [H] Unbounded for-loop bricks transferERC721() 

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-15
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/4
Type: code-finding

## Details
# Handle

toastedsteaksandwich


# Vulnerability details

## Impact
The `nfts` array in the Visor contract could become overpopulated, causing certain functions that loop over it to brick, due to the gas limit. These functions include `transferERC721()` and `getNftIdByTokenIdAndAddr()`. The severity of this issue is increased as the `onERC721Received()` function was missing validation as to whether or not NFTs were actually received, making it easier to exploit this vulnerability. 

## Proof of Concept
The proof of concept code can be found here: https://gist.github.com/toastedsteaksandwich/0443dee7b3db7c9a31a3ede92680e777

The following is included:

1 - A brickpoc.js file, which includes a test case showing that the transferERC721 works, and then filling the `nfts` array with bogus entries to show that the function becomes bricked through a "run out of gas" revert. The gas limit used in the hardhat config is 15m, roughly equal to the current gas limit. The revert is caused by the `_removeNft()` function attempting to run through the `nfts` array.

2 - The sample NFT used - as from https://docs.alchemy.com/alchemy/tutorials/how-to-create-an-nft/how-to-mint-a-nft

3 - The output from the unit tests. 

4 - An updated transferERC721() function - I've slightly modified the transferERC721() function to make the POC easier to produce - I've included the updated function here in the gist for transparency. The modification doesn't affect the vulnerability, it removes access control and locking validation while leaving in the removal of the NFT entry (`_removeNft()`), which is the issue.

## Tools Used
Hardhat with the gas-reporter tool. 

## Recommended Mitigation Steps
To mitigate this issue, the use of an unbounded for-loop should be avoided. This can be done by using a mapping of nftContract=>tokenId=>bool to indicate ownership, instead of using the `nfts` array. 

The `onERC721Received()` function should also be patched to validate whether or not an NFT was actually received. This can be done by validating ownership through the NFT contract and validating that the mapping has not yet been updated. This will avoid representation issues in the code (e.g. having NFT x in the Visor state, but not according to the associated NFT contract).

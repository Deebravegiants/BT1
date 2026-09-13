# [M] The lack of checks in minting NFTs can lead to potential user losses.

## Summary
Severity: Medium
Reporter: Polaris_tow
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L64
Type: audit-issue

## Details
# The lack of checks in minting NFTs can lead to potential user losses.

## Summary
Minted to an address that is a smart contract that can't handle ERC721 tokens will be stuck forever
## Vulnerability Detail
The mint() function below directly calls the _mint() function without checking if the caller is a contract capable of handling ERC721 tokens or if it only allows EOA (Externally Owned Account) calls. For example,` if (tx.origin != msg.sender) revert ContractsNotAllowed()`. If a contract address calls these functions but cannot handle ERC721 tokens correctly, they will get stuck. This can result in a user losing their newly minted tokens forever, which represents a potential loss of value.
```solidity
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }

```
## Impact
This can result in a user losing his newly minted tokens forever, which is a potential values loss. It requires the user to be using a smart contract that does not handle ERC721 properly.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L64
## Tool used

Manual Review

## Recommendation
Replace _mint() with _safeMint() function（Because _safeMint() function performs a check for this.）. Keep in mind this adds a reentrancy possibility, so it is best to add a nonReentrant modifier as well.
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/8b72e20e326078029b92d526ff5a44add2671df1/contracts/token/ERC721/ERC721.sol#L416C1-L447C6

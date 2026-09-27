# [M] NFTs Can Get Locked in the Contracts That Do Not Implement `IERC721Receiver `

## Summary
Severity: Medium
Reporter: ubermensch
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# NFTs Can Get Locked in the Contracts That Do Not Implement `IERC721Receiver `

## Summary
This finding is related to the use of the mint function for minting NFTs, instead of the more secure `safeMint` function.

## Vulnerability Detail
The contract uses the mint function to create new tokens. However, mint does not check if the receiving address can actually receive `ERC721` tokens. If the tokens are sent to a contract that is not prepared to handle them, they could be locked forever. The `safeMint` function, on the other hand, includes a check to ensure that the receiving address is capable of handling the tokens.

## Impact
The impact of this vulnerability is potentially high. If tokens are minted to a contract that cannot handle them, those tokens could be permanently locked and effectively removed from circulation. This could lead to a loss of value for the token holders and could disrupt the functioning of the token ecosystem.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L58-L63

## Tool used
Manual Review

## Recommendation
To mitigate this issue, it is recommended to replace the `_mint` function with the `_safeMint` function in the `MeritNFT` contract. This will ensure that tokens are only minted to addresses that are capable of receiving them, preventing potential loss of tokens.

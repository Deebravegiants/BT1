# [M] potential user losses

## Summary
Severity: Medium
Reporter: Polaris_tow
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L170
Type: audit-issue

## Details
# potential user losses

## Summary
When the quantity of NFTs is limited, it can lead to users' unsuccessful attempts to purchase, resulting in unexpected losses for the users.
## Vulnerability Detail
Below is a detailed explanation of this issue.
The contract restricts the minting quantity of NFTs to 10,000, which is reflected in the code as `uint256 constant public MINT_CAP = 10000`. Suppose the contract has already minted 9,998 NFTs and there are only 2 NFTs remaining. If a user chooses to mint 4 NFTs at this point, it will result in a failed minting transaction. This is an undesirable scenario for the contract. A better logic would be to allow users to purchase the remaining 2 NFTs.
Let's consider another scenario. Suppose a user named Jack discovers that there are 6 NFTs remaining in the contract by using the getAuctionData() function. At this point, Jack decides to purchase 4 NFTs (ideally, Jack would receive 4 NFTs, and the contract would have 2 NFTs remaining). However, at the same time, another user named Alice initiates a transaction to purchase 4 NFTs, and her transaction gets executed on the Ethereum Memory Pool before Jack's transaction.

In this situation, Jack's transaction will fail because Alice's transaction was prioritized and completed first. As a result, there will be 2 NFTs remaining in the contract. Now, if another user named Bob purchases the remaining 2 NFTs (and Bob's transaction is submitted after Jack's), Bob will acquire the remaining 2 NFTs, and Jack will end up empty-handed. This is an undesirable outcome that we want to avoid.

Ideally, we would like to ensure that Jack can mint the remaining 2 NFTs before Bob.
` require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");`
## Impact
 Resulting in unexpected losses for users.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L170
## Tool used
vscode
Manual Review

## Recommendation
When mintedBefore + amount <= MINT_CAP, the user should be able to purchase the remaining NFTs instead of the transaction failing.

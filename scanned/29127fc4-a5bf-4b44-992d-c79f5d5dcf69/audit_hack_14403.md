# [M] Malicious Auctioneer can create an auction with a malicious NFT contract to steal users funds

## Summary
Severity: Medium
Reporter: DevABDee
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
Type: audit-issue

## Details
# Malicious Auctioneer can create an auction with a malicious NFT contract to steal users funds

## Summary
This vulnerability allows malicious auctioneers/owners to exploit a lack of sanity checks and create auctions using malicious NFT contracts, resulting in the theft of users' funds.

## Vulnerability Detail
The `MeritDutchAuction.sol` contract is designed to facilitate auctions exclusively for the `MeritNFT.sol` contract. However, the owner of the MeritDutchAuction contract can set it to any NFT contract address, opening the possibility for a malicious auctioneer to exploit this feature. By setting the address to a malicious implementation, such as one where the `MeritNFT.mint()` function only increments a variable instead of minting actual NFTs. That would result in users calling the `MeritDutchAuction.mint()` function with ETHs without receiving the expected amount of NFTs.
```solidity
   ///@audit owner can set malicious NFT contract to rug pull users!
    function setNFT(address nft_) external onlyOwner {
        require(address(nft) == address(0), "NFT already set");
        nft = MeritNFT(nft_);
    }
```


## Impact
- Loss of funds for the users

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L158

## Tool used
[Shaheen's Vision](https://media.tenor.com/Ypeh_cbxA_gAAAAM/hunt-hunting.gif)

## Recommendation
To address this vulnerability, we recommend considering the following solutions:
1. Implement checks to verify the users' NFT token balances before and after transactions, ensuring that the appropriate number of NFTs are minted.
2. Auctioneer transfers all the NFTs he wants to sell to the `MeritDutchAuction.sol` and then when a user calls `mint()`, the contract transfers the user's specified amount of NFT(s) to the user.
3. Use a Factory system

While any of these three solutions can address the issue, Solution 1 is recommended as it offers a straightforward and effective resolution:
```diff
+      uint256 balanceBefore = nft.balanceOf(msg.sender);
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
+      uint256 balanceAfter = nft.balanceOf(msg.sender);
+      require(balanceAfter == balanceBefore + amount, "minting failed")
```

### Reference:
A similar issue was found in C4's NFT Marketplace Audit: [Malicious Creator can steal from collectors upon minting with a custom NFT contract ](https://github.com/code-423n4/2022-08-foundation-findings/issues/211)

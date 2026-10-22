# [H] MeritDutchAuction.sol - multiple NFTs can be minted by just paying cost of one NFT.

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C14-L128C18
Type: audit-issue

## Details
# MeritDutchAuction.sol - multiple NFTs can be minted by just paying cost of one NFT.

## Summary

[mint](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C14-L128C18) can be called by anyone when the auction is started.
This function takes ETH as pay and mints the NFT to the calleder
But the problem here, during mint call, the call can be re-entered with onERC721Received call. This way user can re-enter again and again and mint all the NFT that will satisfy their NFT limit.

## Vulnerability Detail

```solidity
    function mint(uint256 amount) external payable {
        // Checks
        // Cache mintedBefore to save on sloads
        uint256 mintedBefore = minted;
        // Cache mintedPerAddressBefore to save on sloads
        uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
        // Price being paid is the current price
        uint256 pricePaid = getPrice();
        // Total price being paid is the current price times the amount of NFTs
        uint256 totalPaid = pricePaid * amount;
        // Auction must have started
        require(block.timestamp >= startTime, "Auction not started");
        // Cannot mint more than the mint cap
        require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");
        // Cannot mint more than the cap per address
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
        // Make sure enough ETH was sent in the transaction
        require(msg.value >= totalPaid, "Insufficient funds");


        // Effects
        // Update amount minted in total
        minted += amount;
        // Update amount minted per address
        mintedPerAddress[msg.sender] += amount;
        // Update amount of ETH raised
        totalRaised += totalPaid;


        // Interactions
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender); ---------->> at this call, mint can be re-entered.
        }
...........................

```

## Impact

At the cost of one NFT, all the NFT can be minted by an user till their NFT cap is reached.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C14-L159

## Tool used

Manual Review

## Recommendation

Add non-reentrant protection to mint call.

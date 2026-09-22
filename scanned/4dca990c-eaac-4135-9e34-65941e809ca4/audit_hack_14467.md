# [H] The mint() function can lead to lost funds

## Summary
Severity: High
Reporter: Avci
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# The mint() function can lead to lost funds

## Summary
The mint() function can lead to lost funds.

## Vulnerability Detail
the mint() function is payable so users need to call this function with a native token like eth, for minting the amount of nft that they want. But the issue is this function doesn't handle 0 amount which is can lead to user lost eth.

```solidity
for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
0 amount will skip the minting process and user eth will transfer to contract but don't get any nft.

## Impact
Users will lose their funds if they call the mint() function with zero amount.

## Code Snippet
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
        require(block.timestamp >= startTime, "Auction not started"); //@audit Auction need to check for not end
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
            nft.mint(mintedBefore + i + 1, msg.sender);
        }

        if(msg.value > totalPaid) {
            // If too much ETH was sent, refund the difference
            (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
            require(success, "Refund failed");
        }

        // Emit event for offchain integrations
        emit Minted(msg.sender, amount, pricePaid);
    }
```
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Brain + VS Code

## Recommendation
Consider checking amount != 0

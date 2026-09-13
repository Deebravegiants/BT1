# [M] Front-Running Attack in NFT Minting Process

## Summary
Severity: Medium
Reporter: Elite0x01
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# Front-Running Attack in NFT Minting Process

## Summary
The vulnerability is a front-running attack that can occur during the minting process of NFTs.

## Vulnerability Detail
Front-running refers to the act of an attacker exploiting their position to execute transactions before or alongside legitimate transactions, thereby gaining an unfair advantage.
Let's consider a scenario where the MINT_CAP is about to be reached, with 9996 NFTs already minted and only 4 NFTs left to be minted.

1. Alice sends a transaction to mint 4 NFTs.
2. Bob notices Alice's transaction and submits the same transaction with a higher gas limit.
3. Bob's transaction frontruns Alice's transaction.
4. Bob's transaction is confirmed due to the higher gas fees.
5. Alice's transaction gets reverted because the MINT_CAP has reached its maximum.

## Impact
If the NFT is rare, the attacker can front-run the mint function by using higher gas fees, allowing them to mint the desirable NFT before others.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
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
## Tool used
Manual Review

## Recommendation
Consider implementing a transaction batching mechanism, where multiple mint requests are processed together in a single transaction. This would reduce the chances of front-running attacks by minimizing the time window for attackers to interfere.

# [M] The input amount exceeds the (MINT_CAP-mintedBefore) supply, resulting in the inability to mint NFTs.

## Summary
Severity: Medium
Reporter: ziyou-
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C1-L169C6
Type: audit-issue

## Details
# The input amount exceeds the (MINT_CAP-mintedBefore) supply, resulting in the inability to mint NFTs.

## Summary
The input amount exceeds the (MINT_CAP-mintedBefore) supply, resulting in the inability to mint NFTs.

## Vulnerability Detail
MINT_CAP-mintedBefore=2，alice want to mint 3，but execution unsuccessful.In the next time interval,bob want to mint 2,and successful.
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C1-L169C6
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
@       require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");
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

## Impact
The input amount exceeds the (MINT_CAP-mintedBefore) supply, resulting in the inability to mint NFTs.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C1-L169C6

## Tool used
Manual Review

## Recommendation
It should add a condition to check if `amount + mintedBefore > MINT_CAP`, and if true, mint `MINT_CAP - mintedBefore` tokens.

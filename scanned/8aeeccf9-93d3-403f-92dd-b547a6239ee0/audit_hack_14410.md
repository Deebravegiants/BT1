# [M] Potential zero price could allow user to claim NFTs without paying any amount

## Summary
Severity: Medium
Reporter: caventa
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122-L123
Type: audit-issue

## Details
# Potential zero price could allow user to claim NFTs without paying any amount

## Summary
Potential zero price could allow user to claim NFTs without paying any amount

## Vulnerability Detail
Owner is not trusted. He may set a few possible combination of variables that leads to 0 price. To retrieve the price of a time, see the following function

```solidity
   function getPriceAt(uint256 time) public view returns(uint256) {
        // If auction hasn't started yet, return start price
        if(time < startTime) {
            return startPrice;
        }
        // If auction has ended, return end price
        if(time >= endTime) {
            return endPrice;
        }

        uint256 timePassed = time - startTime;
        uint256 totalSteps = (endTime - startTime) / stepSize;
        uint256 currentStep = timePassed / stepSize;
        uint256 priceRange = startPrice - endPrice;

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
        return price;
    }
```    

Price is determined by startPrice - (priceRange * currentStep / totalSteps); 
From the equation, there are 2 scenarios where price could be 0

a) Start price = 0 and currentStep = 0
b) Start price = n and (priceRange * currentStep / totalSteps) = n

In the mint function, there is no validation to handle price = 0, results in system allows NFTs minting without allowing user to pay any amount.

## Impact
Potential zero price could allow user to claim NFTs without paying any amount

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122-L123
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L137
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L145
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L153
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165

## Tool used
Manual Review

## Recommendation
Change mint function

```solidity
function mint(uint256 amount) external payable {
        // Checks
        // Cache mintedBefore to save on sloads
        uint256 mintedBefore = minted;
        // Cache mintedPerAddressBefore to save on sloads
        uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
        // Price being paid is the current price
        uint256 pricePaid = getPrice();
        +++ require(pricePaid > 0, "Price should be larger than 0"); // audit 
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
            nft.mint(mintedBefore + i + 1, msg.sender); // @audit unable to mint
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

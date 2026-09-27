# [H] MeritDutchAuction.sol : Contract funds can be drained when refunding the excess ETH

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# MeritDutchAuction.sol : Contract funds can be drained when refunding the excess ETH

## Summary

when minting the NFT, user sent the ETH for the amount of NFT wanted to be mint.
When we look at the mint logic, it mints the NFT by taking the ETH as payment. if there is any excess funds, it is refunded to the caller.
During the refund, caller can re-enter again and mint another NFT, this time, they will be refunded again. This way, the ETH from contract can be drained out.

## Vulnerability Detail

Lets looks at the mint logic. Please follow the arrowed comments.

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
            nft.mint(mintedBefore + i + 1, msg.sender); ----------->> NFT is minted.
        }


        if(msg.value > totalPaid) {
            // If too much ETH was sent, refund the difference
              ------------->>> below call.
             (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes("")); 

              ----------->> excess fund is refunded. This time, the receiving contract can have fallback logic which could re-enter to mint again.

            require(success, "Refund failed");
        }


        // Emit event for offchain integrations
        emit Minted(msg.sender, amount, pricePaid);
    }
```

This can be done in just two call.
Lets say,

Bob is the user who wanted to mint 1 NFT with input ETH 100.
The contract has 100 ETH in its balance.

The minting cost of 1 NFT is 10 ETH.

Now, Bob calls and mint 1 NFT, remaining 90ETH is refunded.
Since its low level call, Bob can re-enter again and mint another NFT without any pay. This time again 90 ETH is refunded.

Now the contract will have just 10ETH. 90 ETH is stolen.

## Impact

Loss of funds.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

Add re-entrant protection to mint function.

# [H] Incomplete `mint()` Refund Logic

## Summary
Severity: High
Reporter: moneyversed
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Incomplete `mint()` Refund Logic

## Summary

A vulnerability has been discovered in the MeritDutchAuction contract's mint function which may lead to incomplete refunds in certain edge cases. In these edge cases, the contract might not refund the full amount of overpaid ETH due to the specific logic in the `mint()` function.

## Vulnerability Detail

The `mint()` function in the MeritDutchAuction contract allows users to mint a certain amount of NFTs. The function has a check to ensure that the caller has sent enough ETH to cover the total cost of the minting operation (`msg.value >= totalPaid`). After minting the NFTs, the contract tries to refund any overpaid ETH.

The issue arises in the refund logic, where the contract calculates the overpaid amount as `msg.value - totalPaid`. In a scenario where multiple concurrent transactions try to mint the last remaining NFTs, it is possible that some transactions could overpay the contract without minting any NFTs, as the cap limit would have been reached by other transactions.

## Impact

The impact is financial loss for users. If a user sends more ETH than required to mint the last NFTs, they would not get a full refund. This could lead to potential Ether loss for users in a race condition scenario where multiple transactions are trying to mint the last remaining NFTs at the same time.

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

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

A solution would be to add an additional condition to the refunding logic. If the user has paid enough ETH but the cap limit has already been reached, refund the whole amount (`msg.value`) sent by the user, as no NFTs would be minted in such a case.

## Proof Of Concept

1. Deploy the MeritDutchAuction contract with a MINT_CAP of 1 and a CAP_PER_ADDRESS of 1.
2. Call `setNFT()` function with an address of the deployed MeritNFT contract.
3. Initiate 2 transactions simultaneously:
   1. The first transaction mints the NFT successfully, paying the required ETH.
   2. The second transaction also sends enough ETH to mint an NFT. However, as the MINT_CAP has been reached, this transaction will not mint any NFTs but will have overpaid the contract.

The second transaction will not receive a full refund of the ETH sent, resulting in a financial loss for the user.

**The execution of the transactions simultaneously is needed in order to create a race condition.**

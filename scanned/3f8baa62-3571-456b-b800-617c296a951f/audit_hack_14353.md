# [M] [M-01] `MeritDutchAuction.mint()`: Last few minters maybe DoSed from minting due to other minters even though they called `mint()` first

## Summary
Severity: Medium
Reporter: 0xnevi
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L141
Type: audit-issue

## Details
# [M-01] `MeritDutchAuction.mint()`: Last few minters maybe DoSed from minting due to other minters even though they called `mint()` first

## Summary
Minter that calls `mint()` first may lose last few tokens instead of getting the remaining tokens left due to restrictive maximum NFT cap check.

## Vulnerability Detail
There exists an edge case where the last few minters maybe DoS from minting due to other minters even though they called `mint()` first.

Consider the following scenario:
1. Currently 9996 NFTs have been minted
2. Alice notices 4 NFTs remaining via `getAuctionData()` and calls `mint()`, passing in amount as 4
3. Unknowing to Alice, Bob has called `mint()` to mint the NFT with tokenID of 9997. 
4. Alice's call to `mint()` to mint the remaining 4 tokens reverts since it exceeds the `MINT_CAP`.
4. At the same time, Charlie notices 3 NFTs remaining and calls `mint()`, passing in amount as 3, successfully minting tokenIds 9998, 9999 and 10000
5. Alice did not get any NFTs even though she called `mint()` first and Charlie gets the last 3 NFTs remaining.

In the above scenario, if NFTs are of potentially great value in the future, this could mean potential great loss of funds for Alice due to the unfair missed opportunity to mint the remaining NFT tokens.

## Impact
Minter that calls `mint()` first may lose last few tokens instead of getting the remaining tokens left

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L141

## Tool used

Manual Review

## Recommendation
To prevent this edge case from occuring consider refactoring the MINT_CAP check where if minted amount exceeds cap, we truncate amount minted to at least mint remaining amount of NFT to the minter that calls `mint()` first during the auction. There after, we check that `amount` to be minted is more than 0.
```solidity
function mint(uint256 amount) external payable {
    // Checks
    // Cache mintedBefore to save on sloads
    uint256 mintedBefore = minted;
    // Cache mintedPerAddressBefore to save on sloads
    uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
    // Price being paid is the current price
    uint256 pricePaid = getPrice();
++  // Cannot mint more than mint_cap, if not amount will return 0
++  amount = (mintedBefore + amount > MINT_CAP) ? MINT_CAP - mintedBefore : amount;
++  // Cannot mint 0 amount
++  require(amount > 0, "Cannot mint 0 amount")
    // Total price being paid is the current price times the amount of NFTs
    uint256 totalPaid = pricePaid * amount;
    // Auction must have started
    require(block.timestamp >= startTime, "Auction not started");
--  // Cannot mint more than the mint cap
--  require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");       
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

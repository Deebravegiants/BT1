# [M] CAP_PER_ADDRESS can be circumvented

## Summary
Severity: Medium
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L143
Type: audit-issue

## Details
# CAP_PER_ADDRESS can be circumvented

## Summary
CAP_PER_ADDRESS can be circumvented
## Vulnerability Detail
MeritDutchAuction uses CAP_PER_ADDRESS in order to cap the number of tokens to be minted to an address.
However, this can be circumvented and the existing CAP_PER_ADDRESS requirement doesn't prevent a sybill attack.
An EOA that successfully purchased 4 NFT's can use their other EOA in order to obtain 4 more tokens. Later on, they can even transfer all these 8 NFT's to one address. The auction can be attacked as above until all the NFT's are sold to one entity with many addresses.
## Impact
Tokens can belong to one or a few addresses only rather than desired
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
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L143)
## Tool used

Manual Review

## Recommendation
An unpopular opinion is to make a KYC review for the participants. Else CAP_PER_ADDRESS could be minimized to make this attack a bit delayed.

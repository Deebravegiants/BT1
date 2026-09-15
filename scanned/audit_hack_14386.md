# [H] The function mint() can be `reentrancy` attacked.

## Summary
Severity: High
Reporter: oxchryston
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# The function mint() can be `reentrancy` attacked.

## Summary
The funtion `mint()` can be `frontrun` using the low level call to the `receiver` contract, to steal `nft` from the contract.
## Vulnerability Detail
In the function after the token has been minted to the receiver, if the `msg.value` is more than `totalpaid`, the contract calls  the receiver to refund the excess. This is done using the low level call, through which a malicious user can mint more `nft` to themselves provided that their number of mints has not exceeded the `mintperaddress`. 
```solidity
 function mint(uint256 amount) external payable {
         //...more code.
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
```
## Impact
leads to loss of funds for the protocol.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
## Tool used

Manual Review

## Recommendation
Transfer the excess `eth` in `msg.value` seperately in different functions, to avoid reentrancy.

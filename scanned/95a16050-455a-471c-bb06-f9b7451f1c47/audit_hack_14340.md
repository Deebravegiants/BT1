# [M] Wrong emit value

## Summary
Severity: Medium
Reporter: techOptimizor
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L178
Type: audit-issue

## Details
# Wrong emit value

## Summary
Wrong emit value

## Vulnerability Detail
```solidity
  function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance);
    }
``` 
This will always emit 0 as balance has been transferred to owner

## Impact
Wrong information on frontend or any service making use of it

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L178

## Tool used

Manual Review

## Recommendation
cache the balance of the contract to to a varible and emit it.

# [M] Wrong event emission

## Summary
Severity: Medium
Reporter: sinarette
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L179
Type: audit-issue

## Details
# Wrong event emission

## Summary
`claimProceeds` would always return zero in its event emission.

## Vulnerability Detail
```solidity
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance); //@audit Always Zero
    }
```

After sending all the remaining balance in the contract, `address(this).balance` would always return zero value.

## Impact
Integration with offchain methods would not work as expected

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L179

## Tool used

Manual Review

## Recommendation

Return the exact claimed value.
```diff
    function claimProceeds() external onlyOwner {
+       uint256 exBalance = address(this).balance;
        // Send ETH to the owner
-       (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
+       (bool success, ) = payable(msg.sender).call{value: exBalance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
-       emit ClaimedProceeds(address(this).balance);
+       emit ClaimedProceeds(exBalance);
    }
```

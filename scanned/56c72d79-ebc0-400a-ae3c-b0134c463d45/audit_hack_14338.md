# [M] The `ClaimedProceeds` event doesn't emit the correct balance

## Summary
Severity: Medium
Reporter: blackhole
Source: https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L178
Type: audit-issue

## Details
# The `ClaimedProceeds` event doesn't emit the correct balance


## Summary

There's emitting `ClaimedProceeds` event in the `claimProceeds` function.
But it's using the `address(this).balance` to emit `ClaimedProceeds` event after transferring all balances to the owner's address.
So it's always making `0` balance event.


## Vulnerability Detail

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L178

```solidity
File: src/MeritDutchAuction.sol#L172
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance); // @audit balance is zero?
    }
```

## Impact

Incorrect balance events will cause problems in the offchain integrations.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L178

## Tool used

Manual Review

## Recommendation

Recommend adding a local variable to store balance and using that balance to emit `ClaimedProceeds` event.

```solidity
File: src/MeritDutchAuction.sol#L172
    function claimProceeds() external onlyOwner {
        uint256 balance = address(this).balance;
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(balance);
    }
```

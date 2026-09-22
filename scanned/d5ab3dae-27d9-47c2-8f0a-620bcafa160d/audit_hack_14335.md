# [M] The `ClaimedProceeds` event needs the `to` address parameter

## Summary
Severity: Medium
Reporter: blackhole
Source: https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L41
Type: audit-issue

## Details
# The `ClaimedProceeds` event needs the `to` address parameter


## Summary

Since the `MeritDutchAuction` contract is ownerable, the ownership can be transferred.
Therefore, to properly track claimed events, it is advisable to include the `to` parameter in the `ClaimedProceeds` event.


## Vulnerability Detail

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L41
https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L172

```solidity
File: src/MeritDutchAuction.sol#L45
    event ClaimedProceeds(uint256 amount);

File: src/MeritDutchAuction.sol#L172
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance);
    }
```

## Impact

offchain tracking is difficult without the inclusion of the `to` parameter.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L41
https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L172

## Tool used

Manual Review

## Recommendation

Recommend adding the `to` parameter in the `ClaimedProceeds` event.

```solidity
File: src/MeritDutchAuction.sol#L41
    event ClaimedProceeds(address indexed to, uint256 amount);

File: src/MeritDutchAuction.sol#L172
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(msg.sender, address(this).balance); // @audit here
    }

```

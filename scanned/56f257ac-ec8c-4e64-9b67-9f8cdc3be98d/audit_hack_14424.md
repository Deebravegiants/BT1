# [M] Impossible to integrate with external system

## Summary
Severity: Medium
Reporter: glcanvas
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L171-L179
Type: audit-issue

## Details
# Impossible to integrate with external system

## Summary

Due to `MeritDutchAuction#claimProceeds` at the first transfer all balance from contract's address to owner address the `ClaimedProceeds` event always will have `amount = 0`.
This leads to impossibility to integrate with external system like web-site, because user always will see 0 eth transferred although in fact more has been transferred.

## Vulnerability Detail

Due to `MeritDutchAuction#claimProceeds` at the first transfer all balance from contract's address to owner address the `ClaimedProceeds` event always will have `amount = 0`.
This leads to impossibility to integrate with external system like web-site, because user always will see 0 eth transferred although in fact more has been transferred.

## Impact

It's impossible to integrate any external system (for example web-site) with `MeritDutchAuction` contract

## Code Snippet

Actual code:
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L171-L179

```solidity
    /// @notice Claims the proceeds of the auction, can only be called by the owner
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance); //  <- always will be 0
    }
```
fix with: 

```solidity
    /// @notice Claims the proceeds of the auction, can only be called by the owner
    function claimProceeds() external onlyOwner {
        uint balance = address(this).balance;
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(balance); //  <- will be fine
    }
```

## Tool used

Manual Review

## Recommendation

Fix this error with additional variable, which will be filled before ether transfer.

```solidity
    /// @notice Claims the proceeds of the auction, can only be called by the owner
    function claimProceeds() external onlyOwner {
        uint balance = address(this).balance;
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(balance); //  <- will be fine
    }
```

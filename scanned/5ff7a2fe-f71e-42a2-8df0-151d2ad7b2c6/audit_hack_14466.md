# [M] Issue with wrongly emitted event may cause unexpected behavior in the frontend

## Summary
Severity: Medium
Reporter: devblixt
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172C1-L179C6
Type: audit-issue

## Details
# Issue with wrongly emitted event may cause unexpected behavior in the frontend

## Summary

A wrongly emitted event in MeritDutchAuction contract may result in unexpected behavior in configured frontend. 

## Vulnerability Detail

The claimProceeds function in auction contract transfers the accumulated ETH to the owner and emits the ClaimedProceeds(uint256) event. However, the value passed on to the event while emitting it is the balance of the contract after ETH is transferred to the owner, and hence will always be 0. If a frontend is tracking events, it will detect a ClaimedProceeds() event of 0 ETH and may cause unexpected behavior. The event should have ideally been emitted with the balance of the auction contract before ETH transfer, but is not done so. 

## Impact

Unexpected behavior in the frontend of project dApp can occur, causing confusion for any end user. 

## Code Snippet

The issue is in the claimProceeds function of the auction contract : https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172C1-L179C6

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

## Tool used

Manual Review

## Recommendation

Store the balance of ETH in the contract before transfer, and if transfer is successful, emit the event.

# [M] claimProceeds() event emission will always return 0

## Summary
Severity: Medium
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L177-L178
Type: audit-issue

## Details
# claimProceeds() event emission will always return 0

## Summary
The event is emitted using `address(this).balance` after the entire contract's balance has been sent to the owner. Therefore, the event will always emit **0**:

`emit ClaimedProceeds(0);`

## Vulnerability Detail
The `claimProceeds()` function transfers the entire contract's balance to the owner and then emits the event that, per the docstring: "// Emit event for offchain integrations"

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

Since the balance has already been transferred to the owner, the final call to `address(this).balance` will always be **0**.

## Impact
- Inability to perform offchain integrations

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L177-L178

## Tool used
Manual Review

## Recommendation
Cache the contract balance before transferring and then use the cached balance in the event emission.

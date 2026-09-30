# [M] Incorrect event emitted in MeritDutchAuction

## Summary
Severity: Medium
Reporter: 3agle
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172-L179
Type: audit-issue

## Details
# Incorrect event emitted in MeritDutchAuction

## Summary
The event `ClaimedProceeds` is emitted incorrectly in the `MeritDutchAuction::claimProceeds()`

## Vulnerability Detail
- The `MeritDutchAuction::claimProceeds()` passes current balance of contract as a parameter to the `ClaimedProceeds` event.
- The issue is that this happens after the contract balance is withdrawn
- This leads to the event emitting `Zero` value which might mess up the off chain systems.
- Following is the code snippet from Foundry test where we can see the trace: `emit ClaimedProceeds(amount: 0)`

```bash
 [PASS] testClaimProceeds() (gas: 228940)
Traces:
  [228940] MeritDutchAuctionTest::testClaimProceeds() 
    ├─ [0] VM::startPrank(0x0000000000000000000000000000000FFffFfFF1) 
    │   └─ ← ()
    ├─ [0] VM::warp(86401 [8.64e4]) 
    │   └─ ← ()
    ├─ [196450] MeritDutchAuction::mint{value: 1000000000000000000}(1) 
    │   ├─ [121111] MeritNFT::mint(1, 0x0000000000000000000000000000000FFffFfFF1) 
    │   │   ├─ emit Transfer(from: 0x0000000000000000000000000000000000000000, to: 0x0000000000000000000000000000000FFffFfFF1, tokenId: 1)
    │   │   └─ ← ()
    │   ├─ emit Minted(to: 0x0000000000000000000000000000000FFffFfFF1, amount: 1, price: 1000000000000000000 [1e18])
    │   └─ ← ()
    ├─ [0] VM::stopPrank() 
    │   └─ ← ()
    ├─ [0] VM::startPrank(0x0000000000000000000000000000000FfFFfFFF4) 
    │   └─ ← ()
    ├─ [10494] MeritDutchAuction::claimProceeds() 
    │   ├─ [0] 0x0000000000000000000000000000000FfFFfFFF4::fallback{value: 1000000000000000000}() 
    │   │   └─ ← ()
    │   ├─ emit ClaimedProceeds(amount: 0)
    │   └─ ← ()
    ├─ [0] VM::stopPrank() 
    │   └─ ← ()
    └─ ← ()
```

## Impact
Incorrect event emission will affect off-chain integrations

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172-L179
```solidity
    /// @notice Claims the proceeds of the auction, can only be called by the owner
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{
            value: address(this).balance
        }(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance); //@audit Invalid event emitted
    }
```
## Tool used
Manual Review & Foundry

## Recommendation
- Change the code to the following:
```solidity
    /// @notice Claims the proceeds of the auction, can only be called by the owner
    function claimProceeds() external onlyOwner {
        uint256 balance = address(this).balance;
        
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        
        // Emit event for offchain integrations
        emit ClaimedProceeds(balance);
    }
```

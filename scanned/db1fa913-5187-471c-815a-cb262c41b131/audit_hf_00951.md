# [M] Unhandled exceptions in a function

## Summary
Severity: Medium
Contest weight: 0.6697
Dataset id: 3004
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ApiologyAuctionHouse::_createAuctionWithRandomNumber function, there is a try/catch block that only catches Error(string memory).
```solidity
402: } else {
403:     try apiologyToken.mint() returns (uint256 mintedapDAOId) {
404:         apdaoId = mintedapDAOId;
405:         nftOwners[apdaoId] = address(0);
406:     } catch Error(string memory) {
407:         _pause();
408:         return;
409:     }
410: }
```
This approach is insufficient because the apiologyToken::mint function can be paused, triggering a revert EnforcedPause(); which is not captured by the current try/catch implementation.
```solidity
catch Error(string memory reason) { ... }: This catch clause is executed if the error was caused by revert("reasonString") or require(false, "reasonString") (or an internal error that causes such an exception).
```
As a result, if the token minting is paused, the auction creation process fails, and a new random number request is initiated without verifying the paused state. This oversight leads to unnecessary entropy fee expenditure by the user, as the random number request incurs a cost each time it is called.

## Recommendation
Enhance the try/catch block to handle exceptions related to the paused state.
```solidity
} else {
    try apiologyToken.mint() returns (uint256 mintedapDAOId) {
        apdaoId = mintedapDAOId;
        nftOwners[apdaoId] = address(0);
    } catch {
        _pause();
        return;
    }
}
```

# [M] _previewWithdraw() may fail due to overflow

## Summary
Severity: Medium
Reporter: 8olidity
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L313-L343
Type: audit-issue

## Details
# _previewWithdraw() may fail due to overflow

## Summary
_previewWithdraw may fail due to overflow
## Vulnerability Detail
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L313-L343
```solidity
 for (uint256 i = 1; i <= length; i++) {
      
      ............
      if (
          totalContractsSold + data.size >= auction.totalContracts
      ) {
          // if part of the current order exceeds the total contracts available, partially
          // fill the order, and refund the remainder
          uint256 remainder =
              auction.totalContracts - totalContractsSold;

          cost = lastPrice64x64.mulu(remainder);
          fill += remainder;
      } 
      ..............
      totalContractsSold += data.size;
  }
```
He has totalContractsSold + data.size >= auction.totalcontracts, totalContractsSold += data.size after each loop; As the number of loops increases, there is the possibility of totalContractsSold > auction.TotalContracts.PreviewWithdraw () fails

## Impact
_previewWithdraw may fail due to overflow
## Code Snippet
```solidity
 for (uint256 i = 1; i <= length; i++) {
      
      ............
      if (
          totalContractsSold + data.size >= auction.totalContracts
      ) {
          // if part of the current order exceeds the total contracts available, partially
          // fill the order, and refund the remainder
          uint256 remainder =
              auction.totalContracts - totalContractsSold;

          cost = lastPrice64x64.mulu(remainder);
          fill += remainder;
      } 
      ..............
      totalContractsSold += data.size;
  }
```
## Tool used
vscode
Manual Review

## Recommendation
Determine the TotalContractSSOLD and TotalContracts sizes

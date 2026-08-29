# [M] Pending withdrawal batch debt cannot be payed by the borrower until the cycle end 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-wildcat
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-wildcat-findings/issues/365
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-10-wildcat/blob/c5df665f0bc2ca5df6f06938d66494b11e7bdada/src/market/WildcatMarketBase.sol#L358-L388


# Vulnerability details

## Impact
The borrower will have to pay the interest and fees till the end of the withdrawal cycle. 

## Proof of Concept
To repay a lender who has requested for withdrawal, the borrower is supposed to transfer the assets to the market and call the updateState() function. But _getUpdatedState() function inside the updateState doesn't process the withdrawal batch with the latest available assets unless the batch has been expired.
https://github.com/code-423n4/2023-10-wildcat/blob/c5df665f0bc2ca5df6f06938d66494b11e7bdada/src/market/WildcatMarketBase.sol#L358-L388 
```solidity
  function _getUpdatedState() internal returns (MarketState memory state) {
    state = _state;
    // Handle expired withdrawal batch
    if (state.hasPendingExpiredBatch()) {
      uint256 expiry = state.pendingWithdrawalExpiry;
      // Only accrue interest if time has passed since last update.
      
       ...... more code 

      _processExpiredWithdrawalBatch(state);
    }

    // Apply interest and fees accrued since last update (expiry or previous tx)
    if (block.timestamp != state.lastInterestAccruedTimestamp) {
      (uint256 baseInterestRay, uint256 delinquencyFeeRay, uint256 protocolFee) = state
        .updateScaleFactorAndFees(
          protocolFeeBips,
          delinquencyFeeBips,
          delinquencyGracePeriod,
          block.timestamp
        );
      emit ScaleFactorUpdated(state.scaleFactor, baseInterestRay, delinquencyFeeRay, protocolFee);
    }
  }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-wildcat-findings/issues/365_

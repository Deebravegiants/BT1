# [M] M-12 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-20
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/30
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/ac51cc6102fcf5ab274f8812eb585539332431f4/src/lib/LiquidationHandler.sol#L72


# Vulnerability details

https://github.com/pixeldaogg/florida-contracts/pull/384
This PR adds `getMaxExtension` to address the issue of auction times being indefinitely postponed.

The maximum time is: `block.timestamp` + _liquidationAuctionDuration + `getMaxExtension`

However, `_liquidationAuctionDuration` can be modified, with the current constraint being `_liquidationAuctionDuration < MAX_AUCTION_DURATION (7 days)`

```solidity
    function updateLiquidationAuctionDuration(uint48 _newDuration) external override onlyOwner {
@>      if (_newDuration < MIN_AUCTION_DURATION || _newDuration > MAX_AUCTION_DURATION) {
            revert InvalidDurationError();
        }
        _liquidationAuctionDuration = _newDuration;

        emit LiquidationAuctionDurationUpdated(_newDuration);
    }
```

Therefore, it's still possible that: `block.timestamp` + _liquidationAuctionDuration + `getMaxExtension` could exceed `7 Days`

## Recommended Mitigation

It is recommended to restrict `_liquidationAuctionDuration + ILoanLiquidator(liquidator).getMaxExtension < MAX_AUCTION_DURATION`

```diff
    function updateLiquidationAuctionDuration(uint48 _newDuration) external override onlyOwner {
-       if (_newDuration < MIN_AUCTION_DURATION || _newDuration > MAX_AUCTION_DURATION) {
+       if (_newDuration < MIN_AUCTION_DURATION || _newDuration + ILoanLiquidator(liquidator).getMaxExtension  > MAX_AUCTION_DURATION) {    
            revert InvalidDurationError();
        }
        _liquidationAuctionDuration = _newDuration;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/30_

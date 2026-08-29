# [M] `BufferBinaryOptions._getSettlementFeePercentage()` might revert because of uint underflow when it should work properly.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/149
Type: sherlock-finding

## Details
hansfriese

medium

# `BufferBinaryOptions._getSettlementFeePercentage()` might revert because of uint underflow when it should work properly.

## Summary
`BufferBinaryOptions._getSettlementFeePercentage()` might revert because of uint underflow when it should work properly.

## Vulnerability Detail
While opening a queued trade using [_openQueuedTrade()](https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferRouter.sol#L313), it calls [checkParams()](https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferBinaryOptions.sol#L318) and `_getSettlementFeePercentage()` is used to calculate `settlementFeePercentage` after discounts.

```solidity
    function _getSettlementFeePercentage(
        address referrer,
        address user,
        uint16 baseSettlementFeePercentage,
        uint256 traderNFTId
    )
        internal
        view
        returns (uint256 settlementFeePercentage, bool isReferralValid)
    {
        settlementFeePercentage = baseSettlementFeePercentage;
        uint256 maxStep;
        (isReferralValid, maxStep) = _getSettlementFeeDiscount(
            referrer,
            user,
            traderNFTId
        );
        settlementFeePercentage = //@audit underflow
            settlementFeePercentage -
            (stepSize * maxStep);
    }
```

It calculates the `maxStep` from `NFT Tier` and `referral` and deducts from the original `settlementFeePercentage`.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/149_

# [M] Comptroller _setLinearRateModelAddress does not correctly distribute tokens before update

## Summary
Severity: Medium
Contest weight: 0.5754
Dataset id: 22997
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _setLinearRateModelAddress(LinearRateModel linearRateModel_) public {
    require(msg.sender == admin, "only admin can set Linear Rate Model contract address");
    linearRateModel = linearRateModel_;
    if (address(linearRateModel) != address(0)) {
        // Get new next epoch timestamp
        nextEpochTimestamp = linearRateModel.getNextEpochTimestamp();
    } else {
        bool refreshed = refreshCompSpeeds();
        if (!refreshed) {
            updateMarketsCompIndex(block.timestamp);
        }
        // Set compRate to 0
        compRate = 0;
        refreshMarketsCompSpeeds();
    }
}
```
When updating linearRateModel, the tokens should be distributed according to the old linearRateModel up until the current timestamp, but currently it does not. This would cause two issues:
1. If the new linearRateModel_ != 0, the tokens are not distributed, causing users to receive less Deepr tokens than expected.
2. If the new linearRateModel_ == 0, the linearRateModel is set to zero before token distribution (executing refreshCompSpeeds(), updateMarketsCompIndex()). The core issue is the same: the tokens should be distributed according to the old linearRateModel during updates. Users may receive less Deepr tokens than expected.

## Recommendation
```solidity
function _setLinearRateModelAddress(LinearRateModel linearRateModel_) public {
    require(msg.sender == admin, "only admin can set Linear Rate Model contract address");
    bool refreshed = refreshCompSpeeds();
    if (!refreshed) {
        updateMarketsCompIndex(block.timestamp);
    }
    linearRateModel = linearRateModel_;
    if (address(linearRateModel) != address(0)) {
        // Get new next epoch timestamp
        nextEpochTimestamp = linearRateModel.getNextEpochTimestamp();
    } else {
        // Set compRate to 0
        compRate = 0;
        refreshMarketsCompSpeeds();
    }
}
```

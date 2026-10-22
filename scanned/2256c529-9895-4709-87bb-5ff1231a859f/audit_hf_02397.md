# [M] Precision Issue in Hourly Fee Calculation in Trading

## Summary
Severity: Medium
Contest weight: 0.3984
Dataset id: 12937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function getHourlyFee(Position memory _pos) public view returns(uint256) {
    uint256 timeDeltaInterval = (ChainUtils.getTime() - _pos.lastUpdated) / HOURLY_FEE_INTERVAL;
    return timeDeltaInterval * getHourlyFeeBasisPoints(_pos.indexAsset) * _pos.margin / PRECISION;
}
```
We notice the calculation of the resulting fee (line 798) involves mixed multiplication and division. For improved precision, it is better to calculate the multiplication before the division, i.e., (ChainUtils.getTime()- _pos.lastUpdated) * getHourlyFeeBasisPoints(_pos.indexAsset) * _pos.margin / PRECISION / PRECISION. Note that the resulting precision loss may be just a small number, but it plays a critical role when certain boundary conditions are met. And it is always the preferred choice if we can avoid the precision loss as much as possible.

## Recommendation
Revise the above calculations to better mitigate possible precision loss.

# [M] Proper Utilization Rate Calculation

## Summary
Severity: Medium
Contest weight: 0.3939
Dataset id: 11623
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the same InterestRateModel contract, there is a pure function utilizationRate() that is used to compute the current utilization rate. Our analysis shows that it ignores the passed-in reserves state and computes the utilization rate based on the cash and borrows only.
```solidity
function utilizationRate(
    uint256 cash,
    uint256 borrows,
    uint256 reserves
) public pure returns (uint256) {
    if (borrows == 0) {
        return 0;
    }
    return borrows.mul(100e18).div(cash.add(borrows));
}
```
To elaborate, we show above the related utilizationRate() function. It is our understanding that the utilization rate needs to be computed as borrows / (cash + borrows - reserves), instead of the current implementation of borrows / (cash + borrows) (line 50).

## Recommendation
Revise the utilization rate computation as suggested.

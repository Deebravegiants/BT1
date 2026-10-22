# [M] Possible incorrect utilization rate

## Summary
Severity: Medium
Contest weight: 0.4005
Dataset id: 15752
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In BaseJumpRateModelV2.sol:utilizationRate(), cash, borrows and reserves values are used to calculate the utilization rate. If borrows value is 0, then function will return 0. But in this function the scenario where the value of reserves exceeds cash is not handled. The system does not guarantee that reserves never exceeds cash. The reserves grow automatically over time, so it might be difficult to avoid this entirely.  
```solidity
function utilizationRate(
    uint256 cash,
    uint256 borrows,
    uint256 reserves
) public pure returns (uint256) {
    // Utilization rate is 0 when there are no borrows
    if (borrows == 0) {
        return 0;
    }
    return borrows.mul(1e18).div(cash.add(borrows).sub(reserves));
}
```  
If reserves > cash (and borrows + cash - reserves > 0), the formula for utilizationRate above gives a utilization rate above 1.

## Recommendation
Make the utilization rate computation return 1e18 (which is the maximum utilization rate) if reserves > cash.

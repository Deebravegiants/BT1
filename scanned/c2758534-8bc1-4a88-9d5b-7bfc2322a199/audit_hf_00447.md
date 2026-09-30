# [M] liquidatePosition differs

## Summary
Severity: Medium
Contest weight: 0.5499
Dataset id: 1871
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
liquidatePosition differs between the long and short
Inside the long pool we calculate liquidationThreshold to be 5% of our position principal.
/WasabiLongPool.sol#L156
```solidity
uint256 liquidationThreshold = _position.principal * 5 / 100;
```
However inside the short pool we calculate it as 5% of collateralAmount
/WasabiShortPool.sol#L175
```solidity
uint256 liquidationThreshold = _position.collateralAmount * 5 / 100;
```
where collateralAmount is collateralReceived + _request.downPayment.
In short that means that for longs liquidationThreshold is 5% of what's borrowed and for shorts it's 5% of what's borrowed + 5% of the downpayment.
Short and long liquidation thresholds will be different, where the long will be bigger as it will also include downpayment.

## Recommendation
This difference will increase the short liquidation threshold to beyond what's borrowed.
Consider fixing the discrepancy.

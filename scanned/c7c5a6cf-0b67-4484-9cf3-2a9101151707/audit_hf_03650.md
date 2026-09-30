# [M] Operator can cause fee shares to be minted

## Summary
Severity: Medium
Contest weight: 0.0923
Dataset id: 19730
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When setting the fee rate it is required that the fee recipient is NOT address(0). An operator can bypass this check by changing the fee recipient to address(0) after setting fee.
/Factory.sol#L60-L65
When setting the fee it is required that if the fee != 0 then the fee recipient != address(0)
/Factory.sol#L52-L55
When setting the fee recipient there is no similar check. This means that an operator can bypass the check in setFeeMantissa by setting the fee recipient to address(0) after setting a nonzero fee value.
Operator can bypass fee recipient check

## Recommendation
Implement a check similar to the one in setFeeMantissa that doesn't allow a nonzero fee when fee recipient = address(0)

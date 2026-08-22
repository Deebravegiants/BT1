# [M] cumulativePower check should be inclusive

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/26
Type: code-finding

## Details
# Handle

pauliax


# Vulnerability details

## Impact
Based on my understanding cumulativePower checks should be inclusive to indicate when the threshold is met. Otherwise, there might be impossible to reach it in certain cases (e.g. when 100% power is required). Replace '>' with '>=' in constructor and function checkValidatorSignatures:
if (cumulativePower > _powerThreshold) {
  break;
}
require(
  cumulativePower > _powerThreshold,
  "Submitted validator set signatures do not have enough power."
);

## Recommended Mitigation Steps
cumulativePower >= _powerThreshold

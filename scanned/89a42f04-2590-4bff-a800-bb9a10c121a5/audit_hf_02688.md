# [M] No Minimum Trusted Node Validation

## Summary
Severity: Medium
Contest weight: 0.3813
Dataset id: 14545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When nodes submit information to StaderOracle, there is no validation of a minimum number of trustedNodeOnly roles. Thus as new trusted nodes are being added to the system, an existing node can take advantage and vote for a malicious exchange rate. When early in the setup of StaderOracle, byzantine protection relying on the following can be passed with even just 1 malicious vote;
```solidity
if (
    submissionCount == trustedNodesCount / 2 + 1 &&
    _exchangeRate.reportingBlockNumber > exchangeRate.reportingBlockNumber
)
```

## Recommendation
Testing team recommends validating if a set minimum trusted nodes has been reached before allowing voting to begin.

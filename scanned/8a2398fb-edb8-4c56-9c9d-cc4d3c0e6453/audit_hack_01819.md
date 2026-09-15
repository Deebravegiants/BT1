# [M] Potentially insufficient validation for operator transfers

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

For operator transfers, the current validation does not require the sender to be an operator (as long as the transferred value does not exceed the allowance):


**code/amp-contracts/contracts/Amp.sol:L755-L759**
```solidity
require(
    _isOperatorForPartition(_partition, msg.sender, _from) ||
        (_value <= _allowedByPartition[_partition][_from][msg.sender]),
    EC_53_INSUFFICIENT_ALLOWANCE
);
```

It is unclear if this is the intention or whether the logical `or` should be a logical `and`.

#### Recommendation

Confirm that the code matches the intention. If so, consider documenting the behavior (for instance, by changing the name of function `operatorTransferByPartition`.

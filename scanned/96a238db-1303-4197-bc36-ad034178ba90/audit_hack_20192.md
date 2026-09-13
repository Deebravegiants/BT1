# [H] 6.2.4 Non-zerooperator.limitshould always be greater than or equal tooperator.funded

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** OperatorsRegistry.1.sol#L241, OperatorsRegistry.1.sol#L428-L

**Description:** For the subtraction operation in OperatorsRegistry.1.sol#L428-L430 to not underflow and revert,
there should be an assumption that

```
operators[selectedOperatorIndex].limit >= operators[selectedOperatorIndex].funded
```
Perhaps this is a general assumption, but it is not enforced whensetOperatorLimitsis called with a new set of
limits.

**Recommendation:** Add a check insetOperatorLimitsto enforce the new limits for the operators to be either 0
or in the range[limit, keys].

If these assumptions are not correct, what would having0 < limit < fundedsignify? Also, what would setting
thelimitto 0 whenfundedis positive signify?

**Alluvial:** Implemented in SPEARBIT/3.

**Spearbit:** Acknowledged.

# [H] Inconsistent APR boundary validation between AprPairFeed and Accounting

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23360
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: There is a mismatch between APR boundary validation constants in AprPairFeed and Accounting contracts. The AprPairFeed accepts negative APRs down to -50%, but the Accounting contract rejects any negative APR values, thus data deemed valid by the oracle is rejected during normalization.

```solidity
// AprPairFeed
int64 private constant APR_BOUNDARY_MAX = 2e12; // 200%
int64 private constant APR_BOUNDARY_MIN = -0.5e12; // -50%
/// @dev Validates that the given APR is within acceptable bounds
function ensureValid(int64 answer) internal pure {
    require(
        APR_BOUNDARY_MIN <= answer && answer <= APR_BOUNDARY_MAX,
        "INVALID_APR"
    );
}
```

```solidity
// Accounting
int64 private constant APR_BOUNDARY_MAX = 200e12;
int64 private constant APR_BOUNDARY_MIN = 0;
function normalizeAprFromFeed (/* SD7x12 */ int64 apr) internal pure returns (UD60x18) {
    require(
        APR_BOUNDARY_MIN <= apr && apr <= APR_BOUNDARY_MAX,
        "invalid apr"
    );
}
```

Impact: Protocol DoS: When the feed contains valid negative APR data (between -50% and 0%), the Accounting.normalizeAprFromFeed() function will revert, preventing:
- APR updates via updateAprs();
- Index calculations in updateIndexes();
- Proper accounting updates during deposit/withdrawal flows;

## Recommendation
Recommended Mitigation: Align the two contracts:

```diff
// Accounting.sol
- int64 private constant APR_BOUNDARY_MIN = 0;
+ int64 private constant APR_BOUNDARY_MIN = -0.5e12; // -50%
```

# [M] 5.2.3 GovernorSimpleandVetoGovernorminimum weight math uses the incorrect divisor

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** VetoGovernor.sol#L633-L634, GovernorSimple#L588-L

**Description:** The variableCOMMENT_DENOMINATORis defined in bothGovernorSimpleandVetoGovernorto express
a ratio of 4BPS:

- VetoGovernor.sol#L48-L49:
uint256 public constant override COMMENT_DENOMINATOR = 1_000_000_000;
- VetoGovernor.sol#L633-L634:
uint256 minimumWeight = (escrow.getPastTotalSupply(startTime) * commentWeighting) / 10_000;/// @audit
,! Incorrect denominator, should use`COMMENT_DENOMINATOR`

However, the denominator is left hardcoded as10_000, which would change the minimum comment weight to 40%
of the total supply.

**Recommendation:** Consider changing the math oncommentWeightingto be in BPS, or use theCOMMENT_DENOM-
INATORas it seems that it was intended.

**Velodrome:** Fixed in commit 88861783 by usingCOMMENT_DENOMINATOR.

**Spearbit:** Verified.

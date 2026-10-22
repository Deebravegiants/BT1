# [C] 5.1.4 Changing yield fromClaimablecause fund loss

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** ERC20Rebasing.sol#L

**Description:** IfClaimableyield is changed to any other mode, then users will lose all unclaimed yield. This
happens because changing fromClaimableto any other mode, only takes the fixed part of balance and ignores
the claimable part.

**Recommendation:** While configuring fromClaimableto any other mode, the overall balance (fixed plus claimable)
should be considered as new balance for the new yield mode (while calling_setBalance).

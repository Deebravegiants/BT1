# [H] 5.2.1 Inflated_sharePrice()from inclusion oflockedAmountfunds

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** YieldManager.sol#L348-L

**Description:** The value used for calculation of_sharePrice()istotalValue(), which consists oflockedValue()
andtotalProviderValue().lockedValue(), according to the natspec, is meant to returnthe amount of the
withdrawal token that is held by the yield manager.

This means that the inheritedWithdrawalQueue'slockedAmountis also included, which shouldn't be so. For
theETHYieldManagerspecifically, once requests are finalised,accumulatedNegativeYieldsis decremented if
non-zero, buttotalValue()remains unchanged, sosharePrice()would be inflated for subsequent finalisations
shouldaccumulatedNegativeYieldsbe non-zero.

Finalized ETH is considered to have been burnt on L2 and out of the system on L1 and (part of the) potential
negative yield recovered; solockedAmountfunds should not influence future share prices anymore.

**Recommendation:** Subtract the locked amount invalue.

- uint256 value = totalValue();
+ uint256 value = totalValue() - getLockedAmount();

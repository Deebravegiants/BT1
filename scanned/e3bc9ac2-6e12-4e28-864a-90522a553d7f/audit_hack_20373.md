# [C] 5.1.8 Message can be passed throughOptimismPortalto maliciously callethYieldManager

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** OptimismPortal.sol#L

**Description:** ThroughL2ToL1MessagePasser.initiateWithdrawal(), one can setethYieldManageras the_-
tx.targetto invoke its permissionedrequestWithdrawal()andclaimWithdrawal()methods. The conse-
quences are:

1. Brick existing finalised LIDO withdrawal requests, but yet to be finalised on the bridge viafinalizeWith-
    drawalTransaction(), since they will revert withRequestAlreadyClaimed(_requestId);.
2. Brick the withdrawal queue by requesting a large enough amount such that the cumulative amount is close
    totype(uint128).max, causing subsequentproveWithdrawalTransaction()to revert when it tries to incre-
    ment the cumulative amount.

**Recommendation:** Preventtx.targetfrom being set toyieldManager:

```
if (_tx.target == address(yieldManager)) revert Unauthorized()
```

# DRAFT

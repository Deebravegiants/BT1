# [M] 5.3.6 Fraud recovery logic is missing

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** OptimismPortal.sol#L

**Description:** As per documentation, a partial mitigation for fraud is mentioned as:

```
We can partially mitigate this as the admin by not finalizing withdrawals prior to the fraud period ending.
```
But if theAdmindoesn't finalize the withdrawal, then the withdrawal request will remain stuck in the queue along
with other requests, causing DOS on every user's withdrawal request.

In the end, theAdminwill be forced tofinalizethe fraud request (since withdrawal requests in the queue can't be
skipped). This means that the ETH for said request will be stuck inlockedAmountforever (an attacker also cannot
claim it due to the intervention of the Challenger).

**Recommendation:** Consider adding a new function inOptimismPortalwhich allows theAdminclaiming funds
linked to fraudulent requests and sending funds back to yield manager.

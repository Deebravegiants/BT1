# [M] 6.3.1 Allowed users can directly transfer their share toRedeemManager

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** RedeemManager.1.sol#L280-L281, SharesManager.1.sol#L105 , SharesManager.1.sol#L

**Description:** An allowed user can directly transfer its shares to theRedeemManagerwithout requesting a redeem.
This would cause the withdrawal stack to grow, since the redeem demand (2) which is calculated based on the
RedeemManager's share ofLsETHincreases.RedeemQueuewould be untouched in this case.

In case of an accidental mistake by a user, the locked shares can only be retrieved by a protocol update.

**Recommendation:** Make sureShareManagerwould not allow users to directly transfer their shares to theRedeem-
Managerunless the call totransferFromis made by theRedeemManager.

**Liquid Collective:** Fixed.

**Spearbit:** This issue has been addressed by introducing a storage variableRedeemDemandthat would keep track
of redeem demand for the redeem manager contract:

- commit dda
- commit bc3afe

It does not address the issue that shares can be directly transferred to the redeem manager by a user.

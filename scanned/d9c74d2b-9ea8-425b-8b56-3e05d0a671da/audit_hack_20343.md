# [M] 5.2.14 A malicious collection admin can reclaim a pair at any time to deny enhanced setting royalties

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** StandardSettings.sol#L164-L

**Description:** A collection admin can forcibly/selectively callreclaimPair()prematurely (before the advertised
and agreed upon lockup period) to unilaterally break the settings contract at any time. This will effectively lead to
a DoS to the pair owner for the enhanced royalty terms of the setting despite paying the upfront fee and agreeing
to a fee split in return. This is because theunlockTimeis enforced only on the previous pair owner and not on
collection admins.

A malicious collection admin can advertise very attractive setting royalty terms to entice pair owners to pay a high
upfront fee to sign-up for their settings contract but then force-end the contract prematurely. This will lead to the
pair owner losing the paid upfront fee and the promised attractive royalty terms. A lax pair owner who may not be
actively monitoringSettingsRemovedForPairevents before the lockup period will be surprised at the prematurely
forced settings contract termination by the collection admin, loss of their earlier paid upfront fee and any payments
of default royalty instead of their expected enhanced amounts.

**Recommendation:** EnforceunlockTimeon collection admins authorized byauthAllowedForToken.

**Sudorandom Labs:** Addressed in PR#85.

**Spearbit:** Verified that this is fixed by PR#85.

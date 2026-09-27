# [M] 5.1.1 Governance can remove policy check due to upgradability

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** AddressProvider.sol#L

**Description:** Governance has the possiblity to upgrade the values for several configurations. This allows circum-
venting the Policy checks, due to a bug, mistake, or malicious behaviour. Combined with a lack of security or
checks on other places (e.g. multisig signers, too low a threshold) funds could be lost or stolen.

```
_getAuthorizedAddress(_TRANSACTION_VALIDATOR_HASH)
_getAuthorizedAddress(_TRUSTED_VALIDATOR_HASH)
_getAuthorizedAddress(_POLICY_VALIDATOR_HASH)
```
**Recommendation:** Determine a path to make them immutable, or have a way where an explicit Safe operation
(signed by owner) is required to upgrade to a new version.

**Brahma:** Acknowledged, within the trust scope of governance. Given that the governance and team is known and
not anon, that increases the deterrence of such attacks

**Spearbit:** Acknowledged

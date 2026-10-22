# [M] 5.1.4 Governance can brick Safes by blocking moderator override

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** AddressProvider#L77-L90, SafeModeratorOverridable#L52-L

**Description:** TheSafeModeratorOverridablecontract is a guard that enables additional per-transaction valida-
tion for safes via the policy validator accessed via the transaction validator. Unlike itsSafeModeratorcounterpart,
SafeModeratorOverridableis meant to be overridable allowing the safe owners to override and disable it by
setting theguardback to zero. This is done by:

1. Checking if the attempted safe call is a call tosetGuard(address(0)).
2. Skipping further transaction validation.

The issue with this system is that the override logic is implemented in the separateTransactionValidatorcontract
which is simply called by the safe moderator. The source of truth for the address of the transaction validator is
theAddressProviderwhich thegovernanceaddress can change. This allows a maliciousgovernanceaddress to
effectively take all safes hostage by e.g. changing the "authorized transaction validator" to a contract that blocks
all transactions unless a specific "release ransom" is paid.

**Recommendation:** This should be fixed by moving out the override logic from theTransactionValidatorinto the
immutableSafeModeratorOverridablecontract itself. The override should cause theSafeModeratorOverridable
contract to skip the retrieval of the authorized transaction validator and simply terminate its call successfully such
that the transaction can be executed.

**Brahma:** Solved in PR 62.

**Spearbit:** Verified.

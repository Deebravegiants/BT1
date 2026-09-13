# [M] 6.3.11LibOwnable._setAdminallows settingaddress(0)as the admin of the contract

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** LibOwnable.sol#L8-L10

**Description:** While other contracts likeRiverAddress(for example) do not allowaddress(0)to be used asset
input parameter, there is no similar check insideLibOwnable._setAdmin.

Because of this, contracts that callLibOwnable._setAdminwithaddress(0)will not revert and functions that
should be callable by an admin cannot be called anymore.

This is the list of contracts that import and use theLibOwnablelibrary

- AllowlistV1
- OperatorsRegistryV1
- OracleV1
- RiverV1

**Recommendation:** Consider adding a check insideLibOwnable._setAdminto prevent settingaddress(0)as the
admin, or move that specific check in each contract that import and useLibOwnable.

**Alluvial:** Recommendation implemented in SPEARBIT/11.

**Spearbit:** Note 1: Still missing (client said it will be implemented in other PRs)

- Administrablemiss all natspec comments
- Event for_setAdminare still missing but will be added toInitializableevent in another PR

Note 2: Client has acknowledged that all the contracts that inherit fromAdministrablehave the ability to transfer
ownership, even contracts likeAllowlistV1that didn't have the ability before this PR.

**Alluvial:** Issues in Note 1 addressed in SPEARBIT/33.

**Spearbit:** Acknowledged.

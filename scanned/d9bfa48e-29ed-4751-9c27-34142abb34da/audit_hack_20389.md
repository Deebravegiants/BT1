# [M] 5.3.10donateETHfunds are stuck inOptimismPortal

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** OptimismPortal.sol#L

**Description:** The BlastOptimismPortalinherits thedonateETHfunction from Optimism. It's not needed in Blast
as it was used for the migration to bedrock. The donated funds will be stuck in the contract. When withdrawing,
the withdrawal transaction's ETH is claimed from the yield manager.

**Recommendation:** Consider removing this function if it is not expected to be needed or forward the donated funds
to the yield manager.


# DRAFT

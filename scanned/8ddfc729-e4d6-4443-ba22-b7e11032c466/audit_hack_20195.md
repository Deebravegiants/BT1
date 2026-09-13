# [M] 6.3.12OracleV1.getMemberReportStatusreturns true for non existing oracles

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** Oracle.1.sol#L115-L118

**Description:** memberIndexwill be equal to-1for non-existing oracles, which will cause themaskto be equal to 0 ,
which will cause the function to returntruefor non-existing oracles.

**Recommendation:** Consider changing the function to return false formemberIndex = -1but bear in mind that if
this function is used directly inside some part of the logic it could allow a not existing member to vote. In this case,
the best solution is to always check if the member does not exist by checking ifmemberIndex >= 0.

The function could otherwiserevertif the member does not exist, and returntrue/falseif it does exist and has
voted/not voted. If this solution is chosen, remember that if integrated directly into the code could create a DOS
scenario if not handled correctly.

For all these reasons, consider properly documenting the behavior of the function and the possible side effects in
the natspec comment.


**Alluvial:** Fixed in SPEARBIT/12 by returningfalsefor non-existing oracles.

**Spearbit:** Acknowledged.

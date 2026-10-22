# [M] 5.3.5 getPendingCommits()underreports commits

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** PoolCommitter.sol#L

**Description:** WhenfrontRunningInterval > updateInterval, thePoolCommitter.getAppropriateUpdateIntervalId()
function can returnupdateIntervalIDs that are arbitrarily far into the future, especially ifappropriateIntervalId
> updateIntervalId + 1.

Therefore, commits can also be made to these appropriate interval IDs far in the future by callingcommit(). The
PoolCommitter.getPendingCommits()function only checks the commits forupdateIntervalIdandupdateIn-
tervalId + 1, but needs to check up toupdateIntervalId + factorDifference + 1.

Currently, it is underreporting the pending commits which leads to thecheckInvariantsfunction not checking the
correct values.

**Recommendation:** ThegetPendingCommitsfunction should return all possible pending commits even in the case
wherefrontRunningInterval > updateInterval.

**Tracer:** As part of the CARE program, we found thatgetPendingCommits()can be removed in favour of a running
total of pending mints. This was done and merged into the main repository in PR 315

**Spearbit:** Fix looks good but naming the variabletotalPendingMintsis a bit ambiguous because:

- It sounds like it is a pool token amount but it is a quote token amount. However, the naming for other vars
    (longMintAmountetc.) never distinguished this either, so at least it is consistent.
- It does not include mints fromshortBurnLongMint/longBurnShortMintwhich are also mints. It does not
    include these because you do not need to track it for the invariant checks. You could add a remark here
    about the exclusion

**Tracer:** Addressed in issue 368 and PR 403.

**Spearbit:** Variable names were refactored in PR 403, to indicate if they are in settlement tokens or pool tokens.

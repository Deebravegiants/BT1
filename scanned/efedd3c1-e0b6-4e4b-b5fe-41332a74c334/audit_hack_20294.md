# [H] 5.2.4 Drain tokens condition due to reentrancy incollectFees

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** OrderBook.sol#L800-L
**Description:** collectFeesfunction is not guarded by a re-entrancy guard. In case a transfer of at least one of the
tokens in a trading pair allows to invoke arbitrary code (e.g. token implementing callbacks/hooks), it is possible for
a malicious host to drain trading pools. The re-entrancy condition allows to transfer collected fees multiple times to
both DAO and the host beyond the actual fee counter.
**Recommendation:** Add re-entrancy guard to mitigate the issue incollectFeesfunction or implement acheck-
effect-interactionpattern to update the balance before the transfer is executed.
**Clober:** Fixed in commit 93b287d2.
**Spearbit:** Verified.nonReentrantadded.

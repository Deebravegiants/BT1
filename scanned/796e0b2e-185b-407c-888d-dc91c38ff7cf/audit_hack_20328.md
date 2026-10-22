# [C] 5.1.1 ThecastApprovalBySigandcastDisapprovalBySigfunctions can revert

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** LlamaCore.sol#L683-L
**Description:** ThecastApprovalBySigandcastDisapprovalBySigfunctions are used to cast an approve or
disapprove via an off-chain signature.
Within the_preCastAssertionsa check is performed against thestrategyusingmsg.senderinstead ofpolicy-
holder, the strategy (e.g.AbsoluteStrategy) uses that argument to check if the cast sender is apolicyholder.

```
isApproval
? actionInfo.strategy.isApprovalEnabled(actionInfo, msg.sender)
: actionInfo.strategy.isDisapprovalEnabled(actionInfo, msg.sender);
```
While this works for normal cast, using the ones with signatures will fail as the sender can be anyone who calls the
method with thesignaturesigned off-chain.
**Recommendation:** Consider sending thepolicyholderinstead ofmsg.sender
**Llama:** Fixed in commit 4bb184 and PR 285.
**Spearbit:** Resolved.

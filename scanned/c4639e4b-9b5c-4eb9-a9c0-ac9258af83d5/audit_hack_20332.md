# [M] 5.3.6 The execution opcode of an action can be changed fromcalltodelegate_callafter approval

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LlamaCore.sol#L
**Description:** In Llama anactiononly defines thetargetaddress and the function which should be called. An
actiondoesn't implicitly define if the opcode should be acallor adelegate_call.
This only depends on whether thetargetaddress is added toauthorizedScriptsmapping. However, adding a
targetto theauthorizedScriptscan be done after the approval in a different action.
TheauthorizedScriptaction could use a different set of signers with a different approval strategy.
The change of adding a target toauthorizedScriptshould not impactactionswhich are alreadyapprovedand
in thequeuingstate.
This could lead to security issues when policyholders approved the action under the assumption theopcodewill
be a call instead of a delegate call.
**Recommendation:** If policyholders approve or disapprove of an action, the execution opcode should already be
defined. It should not be possible for other actions with different signers to indirectly change it without explicitly
modifying the current action.
**Llama:** Resolved by commit e2c9ed.
**Spearbit:** Resolved.

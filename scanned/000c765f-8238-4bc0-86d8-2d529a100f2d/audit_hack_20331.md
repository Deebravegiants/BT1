# [M] 5.3.5 LlamaCoredelegate callscan bring Llama into an unusable state

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LlamaCore.sol#L
**Description:** The core contract in Llama allows the execution of actions through adelegate_call.
An action is executed as adelegate_callwhen thetargetis added as anauthorizedScript.
This enables batching multiple tasks into a contract, which can be executed as a single action.
In thedelegate_call, a script contract could modify arbitrary any slot of the core contract.
The Llama team is aware of this fact and has added additional safety-checks to see if theslot0has been modified
by thedelegate_call.
Theslot0contains values that should never be allowed to change.
bytes32 originalStorage = _readSlot0();
(success, result) = actionInfo.target.delegatecall(actionInfo.data);
if (originalStorage != _readSlot0()) revert Slot0Changed();

A script might be intended to modify certain storage slots. However, incorrectSSTOREoperations can completely
break the contracts.
For example, settingactionsCount = type(uint).maxwould prevent creating any new actions, and access to
funds stored in theAccountwould be lost.
**Recommendation:** Users should be aware of the risks associated with using thedelegate_callin the LlamaCore
contract.
We acknowledge the benefits of using adelegate_callin certain situations.
The risks of errors or malicious code in scripts must be clearly documented.
SSTOREoperations in scripts should be reviewed carefully.
To further mitigate these risks, the LlamaCore contract could be separated into two individual contracts.
For not allowing certain variables to be changed at all.
**Llama:** Resolved by adding LlamaExecutor in commit d0ba59 and PR 298.
**Spearbit:** Resolved.

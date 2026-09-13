# [C] 6.1.2 Operators._hasFundableKeysreturnstruefor operators that do not have fundable keys

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** Operators.sol#L149-L

**Description:** Because_hasFundableKeysusesoperator.stoppedin the check, an operator without fundable
keys be validated and returntrue.

Scenario: Op1 has

- keys = 10
- limit = 10
- funded = 10
- stopped = 10

This means that all the keys got funded, but also "exited". Because of how_hasFundableKeysis made, when you
call_hasFundableKeys(op1)it will returntrueeven if the operator does not have keys available to be funded.

By returningtrue, the operator gets wrongly included ingetAllFundablereturned array. That function is critical
because it is the one used bypickNextValidatorsthat picks the next validator to be selected and stake delegate
user ETH.

Because of this issue in_hasFundableKeysalso the issueOperatorsRegistry._getNextValidatorsFromActive-
Operatorscan DOS Alluvial staking if there's an operator withfunded==stoppedandfunded == min(limit,
keys)can happen DOSing the contract that will always makepickNextValidatorsreturn empty.

CheckAppendixfor a test case to reproduce this issue.

**Recommendation:** Alluvial should reimplement the logic ofOperators. _hasFundableKeysthat should return
trueif and only if the operator is active and has fundable keys. The attributestoppedshould not be used.

**Alluvial:** Recommendations implemented in PR SPEARBIT/3.

**Spearbit:** Acknowledged.

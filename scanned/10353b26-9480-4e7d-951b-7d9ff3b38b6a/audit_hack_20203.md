# [H] 5.2.5 Malicious call data can DOSexecute

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Executor.sol#L142-L
**Description:** An attacker can DOS theexecutorcontract by givinginfiniteallowance to normal users. Since
theexecutorincreases allowance before triggering an external call, the tx will always revert if the allowance is
alreadyinfinite.


```
function execute(ExecutorArgs memory _args) external payable override onlyConnext returns (bool, bytes
,! memory) {
if (!isNative && hasValue) {
SafeERC20.safeIncreaseAllowance(IERC20(_args.assetId), _args.to, _args.amount);// reverts if set
,! to`infinite`before
}
(success, returnData) = ExcessivelySafeCall.excessivelySafeCall(...)// can set to`infinite`
,! allowance
}
```
**Recommendation:** Set the allowance to 0 before usingsafeIncreaseAllowance.
Note: also see issueNot always safeApprove(..., 0)
**Connext:** Solved in PR 1550.
**Spearbit:** Verified.

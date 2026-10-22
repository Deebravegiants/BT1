# [M] Calling approve(..., 0) will revert for tokens that do not allow zero approvals

## Summary
Severity: Medium
Contest weight: 0.4419
Dataset id: 13546
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the code, approvals to external contracts are implemented using the following pattern: bool approve = allowanceTarget != address(0); if (approve) currency.approve(allowanceTarget, type(uint256).max); (success, returnData) = target.call{value: value}(data); if (!success) revert CallFailed(returnData); if (approve) currency.approve(allowanceTarget, 0); Using CommandLib._call() as an example, the pattern is: 1. Grant approval to the external contract. 2. Perform the external call. 3. Call approve(..., 0) to revoke any remaining allowance. All instances of this pattern have been listed above. However, calling approve(..., 0) will always revert for tokens that do not allow zero approvals. The most prominent example is BNB:
```solidity
function approve(address _spender, uint256 _value)
returns (bool success) {
    if (_value <= 0) throw;
    allowance[msg.sender][_spender] = _value;
    return true;
}
```
This makes the protocol incompatible with BNB in various parts of the code. For example, when IndexCommandsLib.executeCommands() is used to perform a call to whitelisted exchange proxies with BNB in depositWithCommand(), redeem() or redeemK() of the Index contract, the function call will revert.

## Recommendation
A possible fix would be to only grant the needed allowance before the external call, and after the external call has been performed, check that the remaining allowance is 0 to ensure no dangling approvals are left behind. For example, the CommandTarget struct could be refactored to add an allowanceAmount field, which allows the caller to specify how much allowance to grant. In CommandLib._call(), make the following change as described above:
- bool approve = allowanceTarget != address(0);
- if (approve) currency.approve(allowanceTarget, type(uint256).max);
+ if (allowanceTarget != address(0) && allowanceAmount != 0)
    currency.approve(allowanceTarget, allowanceAmount);
(success, returnData) = target.call{value: value}(data);
if (!success) revert CallFailed(returnData);
- if (approve) currency.approve(allowanceTarget, 0);
+ if (currency.allowance(address(this), allowanceTarget) != 0) revert
    DanglingApproval();
This should be applied to all instances of approve(..., 0) in the codebase. Phuture: Acknowledged, we do not intend to support tokens that do not allow zero approvals.

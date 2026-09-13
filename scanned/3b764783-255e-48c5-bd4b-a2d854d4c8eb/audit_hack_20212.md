# [H] 5.2.16 Malicious call data can steal unclaimed tokens in theExecutorcontract

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Executor.sol#L211
**Description:** Users can provide a destination contractargs.toand arbitrary data_args.callDatawhen doing
a cross-chain transfer. The protocol will provide the allowance to the callee contract and triggers the function call
throughExcessivelySafeCall.excessivelySafeCall.


```
contract Executor is IExecutor {
function execute(ExecutorArgs memory _args) external payable override onlyConnext returns (bool,
,! bytes memory) {
...
SafeERC20.safeIncreaseAllowance(IERC20(_args.assetId), _args.to, _args.amount);
...
// Try to execute the callData
// the low level call will return`false`if its execution reverts
(success, returnData) = ExcessivelySafeCall.excessivelySafeCall(
_args.to,
gas,
isNative? _args.amount : 0,
MAX_COPY,
_args.callData
);
...
}
}
```
Since there aren’t restrictions on the destination contract and calldata, exploiters can steal the tokens from the
executor.
Note: the executor does have excess tokens, see: see: kovan executor.
Note: see issueTokens can get stuck in Executor contract.
Tokens can be stolen by granting an allowance. Setting
calldata = abi.encodeWithSelector(ERC20.approve.selector, exploiter, type(uint256).max);

andargs.to = tokenAddressallows the exploiter to get an infinite allowance of any token, effectively stealing any
unclaimed tokens left in theexecutor.
**Recommendation:** The protocol could communicate with the callee contract through a callback function. A
possible specification of the callback:
function connextExecute(uint32 origin, address adoptedToken, address originSender, uint256 amount,
,! bytes calldata callData) returns(bytes4)

This results in higher gas efficiency because callees do not have to queryorigin,originSender, andamount
through three separate external calls.
Note: this way arbitrary calls are not possible anymore.
**Connext:** New policy: "any funds left in the Executor following a transfer are claimable by anyone". This forces
implementers to think carefully about the calldata. Thus leave the issues as is.
**Spearbit:** Acknowledged.

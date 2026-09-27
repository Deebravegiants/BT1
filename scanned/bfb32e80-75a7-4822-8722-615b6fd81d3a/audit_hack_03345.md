# [H] Dangerous call in DODORouteProxy.externalSwap

## Summary
Severity: High
Reporter: zimu
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L164
Type: audit-issue

## Details
# Dangerous call in DODORouteProxy.externalSwap

## Summary
Although function externalSwap requires swapTarget and approveTarget in white list by checking isWhiteListedContract and isApproveWhiteListedContract, it is still dangerous to perform swapTarget.call if swapTarget has a callback reentrancy.

## Vulnerability Detail
Suppose a hacker calls externalSwap with constructed "bytes memory callDataConcat", a following function calling path can be executed:
1.   externalSwap  -> (success,result) = swapTarget.call{value: fromTokenAmount}(callDataConcat) to a whitelisted contract A;
2.   contract A calls back to externalSwap, and execute _routeWithdraw 1st time;
3.   Then, from contract A return to extenalSwap,  the _routeWithdraw can be executed 2nd time;
This means the hacker can withdraw 2 times, and gain unexpected number of tokens.

## Impact
High. Hacker can obtain unexpected number of tokens.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L164

Reentrancy in DODORouteProxy.externalSwap(address,address,address,address,uint256,uint256,bytes,bytes,uint256) (contracts/SmartRoute/DODORouteProxy.sol#164-229):

	External calls:
	- _routeWithdraw(toToken,receiveAmount,feeData,minReturnAmount) (contracts/SmartRoute/DODORouteProxy.sol#226)
		- to.transfer(amount) (contracts/SmartRoute/lib/UniversalERC20.sol#29)
		- address(msg.sender).transfer(receiveAmount) (contracts/SmartRoute/DODORouteProxy.sol#489)

	External calls sending eth:
	- (success,result) = swapTarget.call{value: fromTokenAmount}(callDataConcat) (contracts/SmartRoute/DODORouteProxy.sol#203-205)
	- _routeWithdraw(toToken,receiveAmount,feeData,minReturnAmount) (contracts/SmartRoute/DODORouteProxy.sol#226)
		- to.transfer(amount) (contracts/SmartRoute/lib/UniversalERC20.sol#29)
		- (success,returndata) = target.call{value: value}(data) (manual-export/@openzeppelin/contracts/utils/Address.sol#135)
		- address(msg.sender).transfer(receiveAmount) (contracts/SmartRoute/DODORouteProxy.sol#489)
	
	Event emitted after the call(s):
	- OrderHistory(fromToken,toToken,msg.sender,fromTokenAmount,receiveAmount) (contracts/SmartRoute/DODORouteProxy.sol#228)
	
## Tool used

Manual Review

## Recommendation

Restrict callDataConcat cannot be constructed arbitarily by indicating to call specified function, using abi.decode and conditional check

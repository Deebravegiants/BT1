# [M] send and transfer do not protect from reentrancies in case of gas price changes

## Summary
Severity: Medium
Reporter: virtualfact
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L323
Type: audit-issue

## Details
# send and transfer do not protect from reentrancies in case of gas price changes

## Summary
In DODORouteProxy.sol, dodoMutliSwap, externalSwap, and mixSwap use send, transfer, and call function without protection from reentrancies. Although send and transfer have limit in gas spending, it cannot deal with gas price changes. So it is better to rewrite these codes using check-effects pattern.

## Vulnerability Detail
These code places using send ,transfer, and call are as follows.

In DODORouteProxy.dodoMutliSwap,
  - _routeWithdraw(toToken,receiveAmount,feeData,minReturnAmount) (contracts/SmartRoute/DODORouteProxy.sol#374)
		  - to.transfer(amount) (contracts/SmartRoute/lib/UniversalERC20.sol#29)
		  - address(msg.sender).transfer(receiveAmount) (contracts/SmartRoute/DODORouteProxy.sol#489)
  - _deposit(msg.sender,assetFrom[0],fromToken,_fromTokenAmount,fromToken == _ETH_ADDRESS_) (contracts/SmartRoute/DODORouteProxy.sol#351-357)
		  - IWETH(_WETH_).deposit{value: amount}() (contracts/SmartRoute/DODORouteProxy.sol#455)
		  - (success,returndata) = target.call{value: value}(data) (manual-export/@openzeppelin/contracts/utils/Address.sol#135)

In DODORouteProxy.externalSwap,
  - _routeWithdraw(toToken,receiveAmount,feeData,minReturnAmount) (contracts/SmartRoute/DODORouteProxy.sol#226)
		- to.transfer(amount) (contracts/SmartRoute/lib/UniversalERC20.sol#29)
		- address(msg.sender).transfer(receiveAmount) (contracts/SmartRoute/DODORouteProxy.sol#489)
  - (success,result) = swapTarget.call{value: fromTokenAmount}(callDataConcat) (contracts/SmartRoute/DODORouteProxy.sol#203-205)

In DODORouteProxy.mixSwap,
- _routeWithdraw(_toToken,receiveAmount,feeData,minReturnAmount) (contracts/SmartRoute/DODORouteProxy.sol#308)
              - to.transfer(amount) (contracts/SmartRoute/lib/UniversalERC20.sol#29)
              - address(msg.sender).transfer(receiveAmount) (contracts/SmartRoute/DODORouteProxy.sol#489)
- _deposit(msg.sender,assetTo[0],_fromToken,_fromTokenAmount,_fromToken == _ETH_ADDRESS_) (contracts/SmartRoute/DODORouteProxy.sol#269-275)
                - IWETH(_WETH_).deposit{value: amount}() (contracts/SmartRoute/DODORouteProxy.sol#455)
                - (success,returndata) = target.call{value: value}(data) (manual-export/@openzeppelin/contracts/utils/Address.sol#135)

## Impact
Medium. Send and transfer, especially call, do not protect reentrancies in case of gas price changes

## Code Snippet
see the following codes
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L323
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L376
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L238

## Tool used
Manual Review

## Recommendation
To rewrite these variables, parameters of send, transfer and call, by using check-effects pattern.
For example,  the follwing code snippet in _routeWithdraw, contracts/SmartRoute/DODORouteProxy.sol
![image](https://user-images.githubusercontent.com/118031646/201474220-a78e00d1-2807-46a6-be5a-c839f9648c00.png)
Suppose receiveAmounts is storage mapping variable, function transfer of above snippet can be rewritten as:
          receiveAmount = receiveAmounts[msg.sender] - routeFee - brokerFee;
          receiveAmounts[msg.sender] = 0;
          ...
          if  (originToToken == _ETH_ADDRESS_)
          {
              ...
              payable(msg.sender).transfer(receiveAmount);
          } else {
              ...
          }

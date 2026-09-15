# [M] Forget to check `minReturnAmount > 0` can let the user bypass the fee when using function `externalSwap`

## Summary
Severity: Medium
Reporter: TrungOre
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L201-L212
Type: audit-issue

## Details
# Forget to check `minReturnAmount > 0` can let the user bypass the fee when using function `externalSwap`

## Summary
Function `externalSwap` doesn't seem like the other 2 swap functions, because it doesn't check if the `minReturnAmount > 0` or not. 

## Vulnerability Detail
Function `externalSwap` let the user pass arbitrary data `callDataConcat` to a black box contract `swapTarget` to make a swap. 
```solidity=
// url = https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L201-L212
{
    require(swapTarget != _DODO_APPROVE_PROXY_, "DODORouteProxy: Risk Target");
    (bool success, bytes memory result) = swapTarget.call{
        value: fromToken == _ETH_ADDRESS_ ? fromTokenAmount : 0
    }(callDataConcat);
    // revert with lowlevel info
    if (success == false) {
        assembly {
            revert(add(result,32),mload(result))
        }
    }
}
```
For example, `swapTarget` can be a dodo V2 pool. A user who makes a swap can specifies the recipient of the swap to his/her address. With this action, the `toToken` won't be transfered to the routeProxy. By setting the `minReturnAmount = 0`, the user can totally make a swap without paying any fee to dodo, cause there is no requirement for variable `minReturnAmount` and the check
```solidity=
// url = https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L485
require(receiveAmount >= minReturnAmount, "DODORouteProxy: Return amount is not enough");
```
in function `_routeWithdraw` still valid because `0 >= 0`. 

## Impact
* User can bypass the fee when use function `externalSwap`. 
* User can use function `externalSwap` for some other purpose on behalf of routeProxy other than swap which may incur some potential risks. 

## Code Snippet
* https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L175-L176
* https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L201-L212

## Tool used
Manual review 

## Recommendation
Add the requirement 
```solidity=
require(minReturnAmount > 0, "DODORouteProxy: RETURN_AMOUNT_ZERO");
```
in function `externalSwap`

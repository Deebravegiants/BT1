# [M] User can execute the mixSwap without paying any fee to dodo by manipulate `assetTo` array

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/34
Type: sherlock-finding

## Details
TrungOre

medium

# User can execute the mixSwap without paying any fee to dodo by manipulate `assetTo` array

## Summary
In the function `mixiSwap`, the user can set the value of `assetTo[mixPairs.length()]` to his/her address to avoid the swapFee incured by dodo's routeProxy. 
**Note:** This issue just happens when the `toToken` is a [ERC777](https://docs.openzeppelin.com/contracts/2.x/api/token/erc777)

## Vulnerability Detail
Function `mixSwap` works based on the assumption that after the swap sequence, the `toToken` will be returned to routeProxy contract, then transferred to the `msg.sender` after deducting the fee.
```javascript=
// Layout of mixswap 
--- User deposit 
--- Do swap - toToken will be transferred to proxyRouter
--- Deduct fee 
--- Transfer the reamaining to sender 
```

Moreover this function allows user to pass arbitrary data of `assetTo`, which indicates where the tokenOut after a single swap will transfer to. And `assetTo[mixiPairs.length()]` will be the destination of `toToken` after swapping through all the pools.
```soldity=
// url: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L234
/// @param assetTo asset Address（pool or proxy）, describe pool adapter's receiver address. Specially assetTo[0] is deposit receiver before all
```
User can set the `assetTo[mixiPairs.length()]` to his/her specified address (maybe a contract they deploy). 

Assume `toToken` is a ERC777, which is a ERC20 support a callback when transferring, user can totally send a small amount of `toToken` to bypass the `minReturnAmount` when (s)he gain the `toToken` after the final swap (Of course, the user will set `minReturnAmount` small as possible).  

Overall, The whole process of this issue is: 
* `toToken` is ERC777 
* user set the `assetTo[mixiPairs.length()]` equal to his/her contract (which support ERC777 callback function)
* user set `minReturnAmount = 1`
* user sends 1 `toToken` to routeProxy after receiving amount of `toToken` of swap 
* dodo take `fee = 1 * routeFeeRate = 0`
* user gets back 1 `toToken` from routeProxy (the remaining `toToken` after deducting fee) 
==> User doesn't need to pay any fee 


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/34_

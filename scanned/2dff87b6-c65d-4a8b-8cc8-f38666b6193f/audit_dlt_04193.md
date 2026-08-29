# [M] Users and brokers can use the protocol without paying fees

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/78
Type: sherlock-finding

## Details
hansfriese

medium

# Users and brokers can use the protocol without paying fees

## Summary

Users and brokers can use the protocol without paying fees

## Vulnerability Detail

The protocol charges fees in the `_routeWithdraw` function and the fee is decided according to the `receiveAmount`.

1. Mix Swap and DODO Mutli Swap
   For simplicity, let us see `mixSwap`.
   A caller is free in selection of `assetTo, mixAdapters, mixPairs` as long as the array lengths match and there are no additional checks.
   So one can create a custom ERC20 token with callback (e.g. `beforeTransfer`) and also a custom simple adapter (with `WETH` and the custom ERC token as base/quote token for example).
   Then he creates a custom contract for the custom token and in the `beforeTransfer` callback he can put custom logic to send a very small amount back to the sender.
   Now if he calls `mixSwap` with his contract address as the last element of `assetTo` (also custom adapter/pair properly and `minReturnAmount=1` or whatever very small), the protocol will process the other swaps normally and finally sends the funds to the custom contract and then the protocol will get very little amount back.
   So the `receiveAmount` becomes very small. Because the fees are calculated by `floor` operations, the protocol will get no fees.

2. External Swap
   A user can call `externalSwap` with arbitrary parameters including `minReturnAmount`, `feeData` and `callDataConcat`.
   Note that for the `externalSwap`, the protocol does not check if `minReturnAmount` is zero.
   And of course the user can set `feeRate` of the `feeData` parameter to zero.
   Now for the `callDataConcat`, one can use any kind of function signature supported by the `swapTarget` and most of the swap protocols expose a function that has a `receiver` parameter.
   One might argue that it is not reasonable because `swapTarget` is an approved one but most of the swap protocols expose this kind of function so it is still worthwhile to explore.
   Below is an example for [1inch](https://github.com/1inch/liquidity-protocol/blob/7ee3f0e88b45bb83ce3981cbe6bad87a4fc13423/contracts/Mooniswap.sol#L255).

   ```solidity
   function swapFor(IERC20 src, IERC20 dst, uint256 amount, uint256 minReturn, address referral, address payable receiver) public payable nonReentrant whenNotShutdown returns(uint256 result) {
       ...
       (confirmed, result, virtualBalances) = _doTransfers(src, dst, amount, minReturn, receiver, balances, fees);
       ...
   }
   ```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/78_

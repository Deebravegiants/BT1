# [M] block.timestamp or deadline

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-amun
Published: 2021-12-14
Source: https://github.com/code-423n4/2021-12-amun-findings/issues/47
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
Some functions, like rebalance() in RebalanceManagerV3 use _deadline as a time limit for swapExactTokensForTokens()
Other functions, like _joinTokenSingle() of SingleTokenJoinV2.sol and _exit() of SingleNativeTokenExitV2() use block.timestamp, although a deadline field is present in the struct.

Possibly the deadline fields should have been used.

## Proof of Concept
https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/callManagers/RebalanceManagerV3.sol#L158-L203
```JS
function rebalance(UnderlyingTrade[] calldata _swapsV2, uint256 _deadline)  external override onlyRebalanceManager {
...
        for (uint256 i; i < _swapsV2.length; i++) {
  ...
            for (uint256 j; j < trade.swaps.length; j++) {
                ..
                _swapUniswapV2(swap.exchange,input,0, swap.path,address(basket), _deadline );
```
https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/callManagers/RebalanceManagerV3.sol#L63-L104
```JS
function _swapUniswapV2(...) {
        basket.singleCall(
            exchange,
            abi.encodeWithSelector(  IUniswapV2Router02(exchange).swapExactTokensForTokens.selector,  quantity,   minReturn,  path, recipient, deadline  ),
            0
        );
```

https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/singleJoinExit/SingleTokenJoinV2.sol#L80-L112
```JS
struct JoinTokenStructV2 {
     ...
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-12-amun-findings/issues/47_

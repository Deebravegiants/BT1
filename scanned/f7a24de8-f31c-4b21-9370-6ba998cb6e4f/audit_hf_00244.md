# [M] block.timestamp or deadline

## Summary
Severity: Medium
Contest weight: 0.6359
Dataset id: 1263
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some functions, like rebalance() in RebalanceManagerV3 use _deadline as a time limit for swapExactTokensForTokens() Other functions, like _joinTokenSingle() of SingleTokenJoinV2.sol and _exit() of SingleNativeTokenExitV2() use block.timestamp, although a deadline field is present in the struct.

Possibly the deadline fields should have been used.

## Proof of Concept
[`RebalanceManagerV3.sol` L158-L203](https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/callManagers/RebalanceManagerV3.sol#L158-L203)

```solidity
function rebalance(UnderlyingTrade[] calldata _swapsV2, uint256 _deadline)  external override onlyRebalanceManager {
...
        for (uint256 i; i < _swapsV2.length; i++) {
  ...
            for (uint256 j; j < trade.swaps.length; j++) {
                ..
                _swapUniswapV2(swap.exchange,input,0, swap.path,address(basket), _deadline );
```

[`RebalanceManagerV3.sol` L63-L104](https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/callManagers/RebalanceManagerV3.sol#L63-L104)

```solidity
function _swapUniswapV2(...) {
        basket.singleCall(
            exchange,
            abi.encodeWithSelector(  IUniswapV2Router02(exchange).swapExactTokensForTokens.selector,  quantity,   minReturn,  path, recipient, deadline  ),
            0
        );
```

[`SingleTokenJoinV2.sol` L80-L112](https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/singleJoinExit/SingleTokenJoinV2.sol#L80-L112)

```solidity
struct JoinTokenStructV2 {
     ...
        uint256 deadline;
     ...
    }
function _joinTokenSingle(JoinTokenStructV2 calldata _joinTokenStruct)  internal {
     ...
           for (uint256 j; j < trade.swaps.length; j++) {
                IPangolinRouter(swap.exchange).swapExactTokensForTokens( amountIn,  0, swap.path, address(this),  block.timestamp );
            }
        }
```

[`SingleNativeTokenExitV2.sol` L59-L88](https://github.com/code-423n4/2021-12-amun/blob/cf890dedf2e43ec787e8e5df65726316fda134a1/contracts/basket/contracts/singleJoinExit/SingleNativeTokenExitV2.sol#L59-L88)

```solidity
struct ExitTokenStructV2 {
        ...
        uint256 deadline;
       ...
    }
function _exit(ExitTokenStructV2 calldata _exitTokenStruct) internal {
     ...
        for (uint256 i; i < _exitTokenStruct.trades.length; i++) {
           ...
            for (uint256 j; j < trade.swaps.length; j++) {
                ...
                IPangolinRouter(swap.exchange).swapExactTokensForTokens( IERC20(swap.path[0]).balanceOf(address(this)), 0, swap.path, address(this), block.timestamp );
            }
        }
```

## Recommendation
Check whether the deadline fields should have been used. If so replace block.timestamp with the appropriate deadline

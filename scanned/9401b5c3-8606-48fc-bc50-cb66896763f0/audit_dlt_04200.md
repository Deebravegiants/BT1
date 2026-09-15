# [M] [Tomo-M5] Transfer zero amount can be reverted

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/66
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M5] Transfer zero amount can be reverted

## Summary

Transfer zero amount can be reverted

## Vulnerability Detail

> Some tokens (e.g. `LEND`) revert when transfering a zero value amount.
> 
> 
> example: [RevertZero.sol](https://github.com/d-xo/weird-erc20/blob/main/src/RevertZero.sol)
> 

Ref: [https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers](https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers)

If the implementation is not designed for such errors, the user will not know the cause of the error.

In the `externalSwap` has no checking the `minReturnAmount` is greater than 0 in spite of the `dodoMutiswap()` and `mixSwap()` has this checking.

Therefore, this case can be happened in the `externalSwap()`

Also, this project assume the any ERC20 so this issue does matter for this project.

```
ERC20: any
ERC721: none
```

Ref: [https://github.com/sherlock-audit/2022-11-dodo-Tomosuke0930#on-chain-context](https://github.com/sherlock-audit/2022-11-dodo-Tomosuke0930#on-chain-context)

## Code Snippet

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L177](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L177)

```solidity
function externalSwap(
        address fromToken,
        address toToken,
        address approveTarget,
        address swapTarget,
        uint256 fromTokenAmount,
        uint256 minReturnAmount,
        bytes memory feeData,
        bytes memory callDataConcat,
        uint256 deadLine
    ) external payable judgeExpired(deadLine) returns (uint256 receiveAmount) {      
        require(isWhiteListedContract[swapTarget], "DODORouteProxy: Not Whitelist Contract");  
        require(isApproveWhiteListedContract[approveTarget], "DODORouteProxy: Not Whitelist Appprove Contract");
				
				/* ... */
```

```solidity
function _multiSwap(
        address[] memory midToken,
        uint256[] memory splitNumber,
        bytes[] memory swapSequence,
        address[] memory assetFrom
    ) internal {
		/* ... */

      // assetFrom[i - 1] is routeProxy when there are more than one pools in this split
      if (assetFrom[i - 1] == address(this)) {
          uint256 curAmount = curTotalAmount * curPoolInfo.weight / curTotalWeight;

          if (curPoolInfo.poolEdition == 1) {
              //For using transferFrom pool (like dodoV1, Curve), pool call transferFrom function to get tokens from adapter
              IERC20(midToken[i]).transfer(curPoolInfo.adapter, curAmount);
          } else {
              //For using transfer pool (like dodoV2), pool determine swapAmount through balanceOf(Token) - reserve
              IERC20(midToken[i]).transfer(curPoolInfo.pool, curAmount);
          }
      }
```

## Tool used

Manual Review

## Recommendation

Add checking the `minReturnAmount` is bigger than 0.

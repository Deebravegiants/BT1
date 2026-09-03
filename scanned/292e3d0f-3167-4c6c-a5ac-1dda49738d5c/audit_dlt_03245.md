# [M] Fee-on-transfer/rebasing tokens will have problems when swapping

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-19
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/359
Type: code-finding

## Details
### Lines of code

--------------

[110](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/CurveSwapper.sol#L110-L142)

### Vulnerability details

-------------

Uniswap v3 does not support [rebasing or fee-on-transfer tokens](https://docs.uniswap.org/concepts/protocol/integration-issues) so using these tokens with it will result funds getting stuck. With fee-on-transfer tokens, if the balance isn't checked, the wrong amount may be transferred out. With rebasing tokens, the contract may have some remaining residual balance after the fixed amount is transferred out. Uniswap v2 does support them but only with the ["SupportingFeeOnTransfer"](https://docs.uniswap.org/contracts/v2/reference/smart-contracts/common-errors#inclusive-fee-on-transfer-tokens) swap variants.

```solidity
File: contracts/Swapper/CurveSwapper.sol

110              yieldBox
111          );
112  
113          // Retrieve tokens from sender or from YieldBox
114          amountIn = _extractTokens(
115              swapData.yieldBoxData,
116              yieldBox,
117              tokenIn,
118              swapData.tokensData.tokenInId,
119              amountIn,
120              swapData.amountData.shareIn
121          );
122  
123          // Swap & compute output
124          amountOut = _swapTokensForTokens(
125              int128(int256(tokenIndexes[0])),
126              int128(int256(tokenIndexes[1])),
127              amountIn,
128              amountOutMin
129          );
130          if (swapData.yieldBoxData.depositToYb) {
131              _safeApprove(tokenOut, address(yieldBox), amountOut);
132              (, shareOut) = yieldBox.depositAsset(
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/359_

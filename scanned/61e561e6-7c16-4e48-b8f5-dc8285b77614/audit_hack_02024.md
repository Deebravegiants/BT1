# [M] 6.5 Incorrect params.amountOutMinimum

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 4 Code Corrected

The parameter params.amountOutMinimum passed to the call to the UniswapV3 adapter in
_openLong() is calculated incorrectly and does not include the leverage.

_openLong executes a swap using the funds of the opened leveraged account given the swap
parameters in longParams. The relevant parameters for the swap are in bytes swapCalldata which
are first extracted and prepared for the call to the swap contract. Note however the parameters
representing amountIn and amountOutMinimum extracted from swapCalldata do not include the
leverage, hence the actual values for the swap have to be calculated:

```
else if (longParams.swapInterface == Constants.UNISWAP_V3) {
ISwapRouter.ExactInputParams memory params = abi.decode(
longParams.swapCalldata,
(ISwapRouter.ExactInputParams)
);
```
```
params.amountIn = leveragedAmount;
params.amountOutMinimum = params
.amountOutMinimum
```

```
.mul(leveragedAmount)
.div(params.amountIn);
ISwapRouter(adapter).exactInput(params);
(, asset) = _extractTokensUniV3(params.path);
}
```
First params.amountIn is overwritten with leveragedAmount. Next params.amountOutMinimum is
calculated, this calculation uses params.amountIn which is equal to leveragedAmount at this point.

Hence the calculation:
params.amountOutMinimum.mul(leveragedAmount).div(params.amountIn); actually is
params.amountOutMinimum.mul(leveragedAmount).div(leveragedAmount); which
simplifies to params.amountOutMinimum.

The leverage is not included in params.amountOutMinimum.

Code corrected:

The calculation of the leveraged value for params.amountOutMinimum is now done correctly using the
unchanged value of the decoded params.amountIn. params.amountIn is only set to
leveragedAmount afterwards.

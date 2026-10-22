# [C] C-10 | UniswapDexAdapter.swapV2Single Doesn't Work

## Summary
Severity: Critical
Contest weight: 0.1914
Dataset id: 22182
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UniswapDexAdapter uses [IUniswapV2Router02.sol](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/interfaces/IUniswapV2Router02.sol#L37-L43) to initiate calls to the V2 Router. In this interface the swapExactTokensForTokensSupportingFeeOnTransferTokens functions is expected to return an array with amounts. However, in the actual [implementation](https://github.com/Uniswap/v2-periphery/blob/0335e8f7e1bd1e8d8329fd300aea2ef2f36dd19f/contracts/UniswapV2Router02.sol#L339C1-L355C6) of that function there are no values returned. This mismatch will result in a revert every time the function is called causing a DOS for the protocol.

## Recommendation
Correct the interface to exclude the returned array.

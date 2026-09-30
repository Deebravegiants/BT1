# [H] MJR-1 Potential safeApprove blocking

## Summary
Severity: High
Contest weight: 0.0466
Dataset id: 4009
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At several places, e.g. Investment.sol#L182 contract perform safeApprove before uniswap's function call, however in case if uniswap doesn't use full provided allowance that can lead to blocking next safeApprove call because safeApprove requires zero allowance.
Another lines with same issue:
Market.sol#L248
Buyback.sol#L125
ProfitSplitter.sol#L195
ProfitSplitter.sol#L204
UniswapMarketMaker.sol#L116
UniswapMarketMaker.sol#L124
UniswapMarketMaker.sol#L125
UniswapMarketMaker.sol#L151
UniswapMarketMaker.sol#L152
UniswapMarketMaker.sol#L181

## Recommendation
We recommend to always reset allowance to zero by calling safeApprove with 0 amount.

# [H] 5.1.2 SwapRouterdoesn't refund unspent ETH after swapping

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** SwapRouter.sol#L106, SwapRouter.sol#L126, SwapRouter.sol#L196, SwapRouter.sol#L

**Description:** SwapRouter allows swapping of ETH for ERC20 tokens. The difference between selling ETH and
an ERC20 token is that the contract can compute and request from the user the exact amount of ERC20 tokens
to sell, but, when selling ETH, the user has to send the entire amount when making the call (i.e. before the actual
amount was computed in the contract). As swaps made viaSwapRoutercan be partial, there are scenarios when
ETH can be spent partially. However, the contract doesn't refund unspent ETH in such scenarios:

1. WhensqrtPriceLimitX96is set (SwapRouter.sol#L80, SwapRouter.sol#L164), the swap will be interrupted
    when the limit price is reached, and some ETH can be left unspent.
2. A swap can be interrupted earlier when there's not enough liquidity in a pool.
3. Positive slippage can result in more efficient swaps, causing exact output swaps to leave some ETH unspent
    (even when it was pre-computed precisely by the caller).

As a result,SwapRoutercan hold some leftover ETH after a swap was made. This ETH can be withdrawn by
anyone via theSwapRouter.refundETH()function, causing a loss to theSwapRouteruser.

**Recommendation:** InSwapRouter.exactInputSingle(),SwapRouter.exactInput(),SwapRouter.exactOutputSingle(),
andSwapRouter.exactOutput()functions, consider returning unspent ETH to the caller at the end of the
functions. ThePeripheryPayments.refundETH()function can be used for that.

**Velodrome:** The recommended fix has been applied in commit 0c5da40e (i.e. a call torefundETH()will be made
at the end of the swap functions insideSwapRouter).

**Spearbit:** Fixed as recommended in commit 0c5da40e.

# [H] Accounting breaks if end market appears mul-

## Summary
Severity: High
Contest weight: 0.6388
Dataset id: 19816
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
accounting breaks
When doing a swap, every market in the provided array of markets has _swap() called, with the input token amount currently residing in the market address of the market, which converts the token to the output token. When the next market isn't array, to be processed on the next iteration, and the pool's balance of input/output market, no transfer is done, but the balance is still updated (to account for tokens being taken out as either a swap order, or a swap into a position's collateral token).
market appears multiple times in the swap path, markets that appear in the array, after the extra destination market, will have updated their accounting of received tokens, without actually receiving tokens.
Token accounting will be broken, because the destination market will have extra tokens that its tracking of its own pool amounts doesn't know about (and can't be updated to know about), and subsequent markets in the chain will have fewer tokens than their pool amount accounting believes it does.
An attacker, if they're willing to incur the expense of swap fees, can perform swaps back and forth through the same market multiple times (to minimize swap impact fees), and cause a pool to have zero collateral tokens remaining, meaning LP market tokens are unable to withdraw their funds because token transfers will revert, and nobody will be able to exit their positions for the affected markets, since no collateral tokens will be available. There also will be an undercollateralization, because the reserves calculation will be wrong.
Even through normal use, if a user does this, they'll be able to get their funds, since LPs are providing swap liquidity, but when it comes time to wind down the market, the last to withdraw will not be able to get their funds.
Tokens aren't transferred to the next market if the next market is the destination market of the swap:
```solidity
// File: gmx-synthetics/contracts/swap/SwapUtils.sol : SwapUtils._swap()
#1
// the amountOut value includes the positive price impact amount
if (_params.receiver != _params.market.marketToken) {
    MarketToken(payable(_params.market.marketToken)).transferOut(
        cache.tokenOut,
        _params.receiver,
        cache.amountOut,
        _params.shouldUnwrapNativeToken
    );
}
cts/swap/SwapUtils.sol#L240-L248
```

## Recommendation
The for-loop calling _swap() already knows when it's processing the last swap, so set a boolean for this fact, and pass that variable into _swap(), and check the variable rather than using the current check

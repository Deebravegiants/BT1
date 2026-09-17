# [M] Deadline set to `block.timestamp` is problematic

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L113C1-L119C6
Type: audit-issue

## Details
# Deadline set to `block.timestamp` is problematic

## Summary
**Remember**
> Because Front-running is a key aspect of AMM design, deadline is a useful tool to ensure that your tx cannot be “saved for later”.
Due to the removal of the check, it may be more profitable for a miner to deny the transaction from being mined until the transaction incurs the maximum amount of slippage.

Most of the functions that interact with UniswapV3 do not have a deadline parameter, but specifically, the one in the SwapRouter.vy,  is passing block.timestamp to a UniswapV3 router, which means that whenever the miner decides to include the txn in a block, it will be valid at that time, since block.timestamp will be the current timestamp.
## Vulnerability Detail
Here it sets the deadline to block.timestamp,
```vyper 
    fee: uint24 = self.direct_route[_token_in][_token_out]
    assert fee != 0, "no direct route"

    params: ExactInputSingleParams = ExactInputSingleParams(
        {
            tokenIn: _token_in,
            tokenOut: _token_out,
            fee: fee,
            recipient: msg.sender,
            deadline: block.timestamp,
            amountIn: _amount_in,
            amountOutMinimum: _min_amount_out,
            sqrtPriceLimitX96: 0,
        }
    )
    return UniswapV3SwapRouter(UNISWAP_ROUTER).exactInputSingle(params)
```
## Impact
Advanced protocols like Automated Market Makers (AMMs) Uniswap can allow users to specify a deadline parameter that enforces a time limit by which the transaction must be executed. Without a deadline parameter, the transaction may sit in the mempool and be executed at a much later time potentially resulting in a worse price for the user.
Protocols shouldn't set the deadline to block.timestamp [[more on this](https://blog.bytes032.xyz/p/why-you-should-stop-using-block-timestamp-as-deadline-in-swaps)] as a validator can hold the transaction and the block it is eventually put into will be block.timestamp, so this offers no protection.
## Code Snippet
The following are instances of such
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L113C1-L119C6
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L88C1-L95C34

## Tool used

Manual Review

## Recommendation
Add deadline arguments to all functions that interact with the SwapRouter.vy, and pass it along to SwapRouter.vy calls.

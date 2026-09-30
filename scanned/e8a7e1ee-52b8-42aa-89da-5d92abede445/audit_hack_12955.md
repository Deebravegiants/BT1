# [M] Missing `deadline` checks for UniswapV3SwapRouter allow pending transactions to be maliciously executed

## Summary
Severity: Medium
Reporter: Vagner
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L92
Type: audit-issue

## Details
# Missing `deadline` checks for UniswapV3SwapRouter allow pending transactions to be maliciously executed

## Summary
All the swaps done in the `SwapRouter.vy` , `Dca.vy` and `LimitOrders.vy` are setting the `deadline` check to `block.timestamp` which basically disables the ability of the user to protect themselves against their trades to be maliciously executed at a later point.
## Vulnerability Detail
The contracts specified above interact with the `UniswapV3SwapRouter` to swap some tokens for other tokens by calling the `exactInput` with the necessary params. The `ExactInputParams` also has a `deadline` param which is used to protect users against unknowingly making bad trades, in case their transaction gets executed at a way later point because of the low gas fee paid.
## Impact
Imagine this simple situation:
- Bob wants to execute any swap function, which calls the `swap` function in the `SwapRouter,vy`, and wants to swap 1500 ARB for 1 WETH, later swapping that WETH for 2000 USDC or USDT. He signs the transaction setting the `_min_amount_out` to 0.99 WETH to allow a minimum amount of slippage.
- The transaction is submitted to the mempool, however, Bob chose a transaction fee that is too low for miners to be interested in including his transaction in a block. The transaction stays pending in the mempool for extended periods, which could be hours, days, weeks, or even longer.
- When the average gas fee dropped far enough for Bob's transaction to become interesting again for miners to include it, his swap will be executed. In the meantime, the price of WETH could have drastically changed. He will still at least get 0.99 ETH due to `_min_amount_out`, but the USDC/USDT value of that output might be significantly lower. He has unknowingly performed a bad trade due to the pending transaction that stayed in the mempool for too long.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L92
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L115
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L218
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L176
## Tool used

Manual Review

## Recommendation
Introduce a `deadline` parameter to all of the functions that uses the `swap` method to protect the users, since even if Arbitrum uses  the Sequencer to send a batch of transactions to the L1 Ethereum very fast, the Sequencer  can be down for periods of time which will make the transactions taking way longer than they are supposed to.

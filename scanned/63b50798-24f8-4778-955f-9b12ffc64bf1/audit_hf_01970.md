# [H] addLiquidityEth() and swapExactTokensForETHSupportingFeeOnTransferTokens are vulnerable to MEV

## Summary
Severity: High
Contest weight: 0.2227
Dataset id: 11114
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
addLiquidityEth() should specify amountTokenMin and amountETHMin to prevent transactions frontrunning it, changing the price and getting less lp tokens in return. Additionally, the deadline argument should be sent as an argument to launch() instead of using block.timestamp. When block.timestamp is used, validators may include the transaction whenever they want, such that the price could have changed significantly by then.
swapExactTokensForETHSupportingFeeOnTransferTokens() also specifies the minimum ETH amount out as argument, but currently it is set to 0. The deadline is also block.timestamp.

## Recommendation
When adding liquidity, amountTokenMin and amountETHmin should be sent as a percentage of the total supplied ETH and Ordiswap tokens, respectively, so the price can't fluctuate more than the defined percentage.
When swapping, the price should ideally be fetched off chain and sent as argument to a swap() call in the OrdiswapToken contract. In fact, the current design choice of swapping when users transfer funds and the fees reach the threshold may lead to poor UX as users can't fully predict if their transfer will trigger the swap, possibly leading to reverts. Create a separate onlyOwner swap function that will swap the OrdiswapToken for ETH when the owner wants.
A good rule of thumb for the deadline argument is using 30 minutes after the block.timestamp, calculated off chain and sent to launch() and the new swap() onlyOwner.

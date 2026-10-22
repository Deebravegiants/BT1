# [H] VLT-1 | restETH Becomes Cheaper Upon Withdrawals

## Summary
Severity: High
Contest weight: 0.2174
Dataset id: 20579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the completeWithdraw function the restETH shares are only burned upon completion of the withdrawal. However the shares attributed to the Vault contract in the Eigenlayer StrategyManager contract are reduced upon the queuing of a withdrawal. The strategy contract will often refer to the StrategyManager.stakerStrategyShares to produce the shares result (see [StrategyBase)](https://github.com/Layr-Labs/eigenlayer-contracts/blob/m2-mainnet/src/contracts/strategies/StrategyBase.sol). Therefore the totalAssets value is reduced immediately upon calling the withdrawUsingEiganShares function, while the corresponding decrease in the restETH supply only occurs when the withdrawal is completed in the completeWithdraw function. As a result, the price of restETH will errantly drop when users initiate a withdrawal with the withdrawUsingEiganShares function.

## Recommendation
Reduce the shares of restETH immediately in the withdrawUsingEiganShares function, as this is when the corresponding reduction in totalAssets occurs.

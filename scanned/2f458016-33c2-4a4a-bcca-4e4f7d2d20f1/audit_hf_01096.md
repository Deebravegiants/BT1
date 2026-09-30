# [M] Lack of slippage protection in buy and sell functions

## Summary
Severity: Medium
Contest weight: 0.1254
Dataset id: 4200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The buy and sell functions in the BondingCurve contract currently lack slippage protection mechanisms. These functions are integral to the contract's operation as they facilitate the purchase and sale of tokens based on a bonding curve model, which acts similarly to an Automated Market Maker (AMM). The absence of slippage protection can lead to users receiving fewer tokens or less Ether than expected due to price fluctuations between the time a transaction is initiated and when it is executed. This can result in a poor user experience and potential financial loss.

## Recommendation
To mitigate the risk of slippage, it is recommended to introduce parameters for minimum acceptable amounts in both the buy and sell functions. Specifically, the buy function should include a minTokens parameter, which specifies the minimum number of tokens the user expects to receive. Similarly, the sell function should incorporate a minEthers parameter, indicating the minimum amount of Ether the user expects to receive. Additionally, view functions should be implemented to allow users and frontends to compute these minimum amounts before executing a transaction. This will ensure that transactions are only executed if the expected outcomes are met, thereby protecting users from adverse price movements.

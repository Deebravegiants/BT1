# [H] GLOBAL-2 | Anyone May performUpkeep

## Summary
Severity: High
Contest weight: 0.1617
Dataset id: 19262
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no access control for the performUpkeep function, therefore any arbitrary address may execute an order. On a network with a public mempool, such as Avalanche, any arbitrary user may observe the Chainlink keeper’s transaction and copy the performData to execute their own deposit, withdrawal, or order. A malicious actor can therefore front-run the execution of other user’s orders to manipulate price impact such that the actor stands to gain a profit at the user’s detriment.

## Recommendation
Add access controls to the performUpkeep function in the MarketAutomation, DepositAutomation, and WithdrawalAutomation contracts. Once access controls are added to the performUpkeep function, it should be noted that the permissioned caller still holds the ability to decide execution ordering, controlling the price impact experienced by orders.

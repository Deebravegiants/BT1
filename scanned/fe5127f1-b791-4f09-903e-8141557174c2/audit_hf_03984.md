# [M] Liquidation process is flawed. missing incen-

## Summary
Severity: Medium
Contest weight: 0.1577
Dataset id: 20352
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Aloe protocol has a Liquidation process, which involves a grace period for the Borrower. This means, there is a warn function, that has to be called, that is setting a unleashLiquidationTime. A Liquidation can only be executed when this time is reached. Problem is, there is no incentive for anyone to call the warn function. Only the actual liquidate function is inventiviced by giving a 5% incentive in Tokens, if there is a swap required, and always giving a small amount of ETH (ANTE) to cover the gas cost. A Liquidator that calls the warn function has no guarantee, that he is the one, that actually can call liquidate, when the time has come. Therefore it would be a waste of Gas to call the warn function. This might result in a situation where nobody is willing to call warn, and therefore the borrower will not get liquidated at all, which could ultimately lead to a loss of Funds for the Lender, when the Borrower starts to accrue bad Debt.
• No incentive to call warn --> Borrower will not get liquidated
• Loss of funds for Lender, because Borrower might accrue bad debt

## Recommendation
Incentivice the call of warn, to at least pay a small amount of eth (similiar to the ANTE), to ensure liquidation is going to happen.

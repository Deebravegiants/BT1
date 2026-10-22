# [H] Incorrect blocksPerYear constant leads to wrong calculations

## Summary
Severity: High
Contest weight: 0.2319
Dataset id: 15748
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect blocksPerYear constant in JumpRateModel leads to wrong calculations. As discussed with the dev team, and as can be seen from the docs, the protocol will be deployed on L2 chains (Meter, Base) as well as on the ETH Mainnet. The JumpRateModel is forked from Compound which was designed to be deployed on the ETH Mainnet. The problem is that the blocksPerYear constant which is used to calculate the interest rate on a per-block basis is set to 2102400:  
uint256 public constant blocksPerYear = 2102400;  
The number assumes that the block time is 15 seconds which is wrong for the L2 chains. The average block time on Meter is 1.93 sec while on BASE is 2 sec hence the blocksPerYear number should be much higher. Because of that the baseRatePerBlock and multiplierPerBlock will be affected and will be much higher. This will lead to inflating getBorrowRate which directly affects other critical functions of the protocol.

## Recommendation
Depending on which chain the project is deployed, pass the value for blocksPerYear in the constructor as it is done for the other interest rate models.  
SumerMoney_report.md

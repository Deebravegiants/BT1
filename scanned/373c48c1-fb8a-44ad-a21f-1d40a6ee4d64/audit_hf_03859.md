# [M] User will be forced liquidated

## Summary
Severity: Medium
Contest weight: 0.2433
Dataset id: 20119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The addMargin function have a vulnerability that can potentially lead to issues when the contract is paused. Users are unable to add margin during the paused state, which can leave them vulnerable to liquidation if their collateral value falls below the required threshold. Additionally, after the contract is unpaused, users can be subject to frontrunning, where their margin addition transactions can be exploited by other users.  
To better understand how this vulnerabilities could be exploited, let's consider a scenario:  
1): The contract owner pauses the contract due to some unforeseen circumstances or for maintenance purposes.  
2): During the paused state, User A wants to add margin to their account. However, they are unable to do so since the contract prohibits margin addition while paused.  
3): Meanwhile, the price of the collateral supporting User A's account experiences significant fluctuations, causing the value of their collateral to fall below the required threshold for maintenance.  
4): While the contract is still paused, User A's account becomes eligible for liquidation.  
5): After some time, the contract owner decides to unpause the contract, allowing normal operations to resume.  
6): User A tries to add margin to their account after the contract is unpaused. However, before their transaction is processed, User B, who has been monitoring the pending transactions, notices User A's margin addition transaction and quickly frontruns it by submitting a higher gas price transaction to liquidate User A's account instead.  
Now userA will be forcefully liquidated even tho he wants to add the margin.  
You can read more from this link  
The identified impact could be  
1): Unfair Liquidations: Users can be unfairly liquidated if their margin addition transactions are frontrun by other users after the contract is unpaused. This can result in the loss of their collateral.

## Recommendation
Implement a Fair Liquidation Mechanism: Introduce a delay or waiting period before executing liquidation transactions. This waiting period should provide sufficient time for users to address their collateral issues or add margin.

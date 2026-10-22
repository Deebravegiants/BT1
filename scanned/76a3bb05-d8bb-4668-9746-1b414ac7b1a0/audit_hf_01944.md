# [M] Insurance timelock is flawed

## Summary
Severity: Medium
Contest weight: 0.1363
Dataset id: 10721
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user deposits in the swappool, the latest deposit block number is registered. This is to prevent users from immediately redeeming swappool lp tokens for backstop assets through the backstopBurn function without first waiting for the needed insurance period. However, the way this is tracked, involves a direct mapping of the block.number to the sender, as such, every new deposit a user makes overwrites the previously tracked block.number. As result, serious pool depositors will be forced to wait longer for time periods before being able to redeem their lptokens.  
function deposit(  
//...  
latestDepositAtBlockNo[msg.sender] = block.number;  
//...  
_processDeposit(_depositAmount, sharesToMint_);  
//...  
The same can be observed in the initiateWithdraw function in BackstopPoolCore.sol, and appears to be by design based on the code comment on the function.

## Recommendation
Recommend tracking each deposit with an id, and its corresponding block.number instead. That way, users, especially constant pool depositors will not be forced to endure longer waiting periods.

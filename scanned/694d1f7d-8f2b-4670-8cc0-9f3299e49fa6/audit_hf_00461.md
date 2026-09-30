# [M] In OracleLess.createOrder() fee-

## Summary
Severity: Medium
Contest weight: 0.1376
Dataset id: 1892
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The max value of feeBips should be <=10000. But this validation is missing in createOrder(). All such orders where feeBips is > 10000 will revert in execute() method. A malicious user can create 100s of such orders which never execute even if the price conditions are met. It can use USDC as tokenIn and blacklist itself so that _cancelOrder() also reverts. As _cancelOrder() tries to transfer tokenIn to user. If the receiver is blacklisted user then transfer will fail. This was the malicious user can create 1 wei orders will can neither execute nor cancellable.
ntracts/automatedTrigger/OracleLess.sol#L38C5-L67C6

Missing feeBips input validation in createOrder()

Internal pre-conditions  

External pre-conditions  

Attack Path  
Such orders will exist in the pendingOrderIds which can not be deleted from the queue. These orders can increase the queue size until the max gas usage limit is reached. Which will DoS all other orders.

## Recommendation
Add the check feeBips <= 10000 in createOrder() of OracelLess.sol.

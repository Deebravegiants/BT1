# [H] Native ETH Restake Admin Can Drain Funds By Manipulating tx.gasprice

## Summary
Severity: High
Contest weight: 0.7624
Dataset id: 14450
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The native ETH restake admin can drain ETH from DepositQueue and OperatorDelegator by manipulating the tx.gasprice to receive a higher gas refund. This can be proﬁtably exploited by colluding with a block proposer.
The gas refunding mechanism in DepositQueue and OperatorDelegator uses tx.gasprice to calculate the amount of ETH to refund back to the caller:
DepositQueue
```solidity
uint256 gasUsed = (initialGas - gasleft()) * tx.gasprice;
uint256 gasRefund = address(this).balance >= gasUsed ? gasUsed : address(this).balance;
```
OperatorDelegator
```solidity
uint256 gasSpent = (initialGas - gasleft() + baseGasAmountSpent) * tx.gasprice;
adminGasSpentInWei[msg.sender] += gasSpent;
```
However, tx.gasprice returns the effective_gas_price which is calculated after EIP-1559 as follows:
```solidity
priority_fee_per_gas = min(transaction.max_priority_fee_per_gas, transaction.max_fee_per_gas - block.base_fee_per_gas)
effective_gas_price = priority_fee_per_gas + block.base_fee_per_gas
```
Since transaction.max_priority_fee_per_gas and transaction.max_fee_per_gas are set by the transaction origina­tor, it is possible to manipulate tx.gasprice by setting these values unrealistically high.
The transaction’s priority fee is sent to the block proposer, so a malicious native ETH restake admin can collude with a block proposer such that the exploit can be proﬁtable for both parties.

## Recommendation
Consider using block.basefee instead of tx.gasprice to calculate the gas refund.

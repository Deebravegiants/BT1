# [M] Maradona: Excess msg.value not refunded to

## Summary
Severity: Medium
Contest weight: 0.4374
Dataset id: 22794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Maradona.takeTokensAndTrade(), excess msg.value is not refunded to the user, which may leave some Ethers stuck in the contract. In Maradona.takeTokensAndTrade(), excess msg.value is not refunded to the user. If the output token is not ETH, the contract will send the user the entire balance of the output token only, but not ETH. Per the contest README: We need to monitor specially that there is no set of inputs that allows a transaction to succeed if the balance of the contracts involved in after the transaction is greater than before the transaction. This means that we want that always balance before trading is equal to balance after trading for all contracts for all tokens. language that indicates the codebase's restrictions and/or expected functionality. Issues that break these statements, irrespective of whether the impact is low/unknown, will be assigned Medium severity. Thus, this issue breaks an invariant defined by the protocol Breaks invariant defined by the protocol, funds may remain in the contract

## Proof of Concept
In the file Maradona.test.ts, modify line 537 to the following: 
```solidity
{ }
```
Which will make the tx sends twice the amount of Ethers required. Running the test with make tests/Maradona gives the following failed test: Which shows that the tx does indeed go through, and the assertion at line 543 shows that ETH indeed remains in the contract

## Recommendation
After all operations have succeeded, refund the contract's entire ETH balance back to msg.sender

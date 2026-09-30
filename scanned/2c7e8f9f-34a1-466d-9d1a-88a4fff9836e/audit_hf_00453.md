# [M] btc fee miscalculation may lead

## Summary
Severity: Medium
Contest weight: 0.1105
Dataset id: 1879
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling btcSignAndSend to send tokens to users when target network is bitcoin, the transaction fee is evaluated based on inputs and outputs, unfortunately the output struct size is not correctly accounted for. This may lead to insufficient fee provided for a transaction to be included, and either DoS or unexpected delays.
```go
util_btc.go#L87:
txSize := int64(10 + (len(tx.TxIn) * 297) + (len(outputs) + 1*32))
```
We can see that len(outputs) is not multiplied by output structure length in bytes which we can assume to be 32.
Internal pre-conditions
External pre-conditions
Attack Path
Some outbound transfers (from the bridge) may fail unexpectedly

## Recommendation
Consider modifying the txSize calculation:
```diff
util_btc.go#L87:
- txSize := int64(10 + (len(tx.TxIn) * 297) + (len(outputs) + 1*32))
+ txSize := int64(10 + (len(tx.TxIn) * 297) + ((len(outputs) + 1)*32))
```

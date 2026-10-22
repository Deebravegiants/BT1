# [M] Caller does not receive excess gas fee inStargateManage

## Summary
Severity: Medium
Contest weight: 0.1258
Dataset id: 22792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The original caller does not receive excess gas fees in StargateManager. In StargateManager::bridge, the refundAddress is always set to the StargateManager address payable refundAddress = payable(address(this)); This means any excess gas used for sending the cross chain swap message is refunded to StargateManager and only the owner can retrieve this despite the fact that the bridging was provided by the caller for which the bridging transaction is being executed on behalf of (via a paymaster) - this is a problem when called via getBridgeFee quotes the required bridging fee with a non-empty payload of length 2 despite the actual swap being sent with an empty payload, causing excess gas to be sent which should be sent back to the user. Caller does not receive excess gas fees resulting from bridging with StargateManager.

## Recommendation
Set refundAddress to an address provided by the caller of the paymaster (e.g. in extraAddresses).

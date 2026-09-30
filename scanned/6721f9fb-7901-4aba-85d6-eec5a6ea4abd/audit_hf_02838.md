# [M] A client can lose money if it is removed from the whitelist

## Summary
Severity: Medium
Contest weight: 0.3935
Dataset id: 15794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a client is removed from the whitelist, it loses access to the functions inside of the smart contracts. This is a problem when a client is removed but still have funds deposited in the DepositContract. Thus, the client will not be able to withdraw his funds because of the first require statement in withdrawFundClient:

```solidity
function withdrawFundClient(uint256 _amount) external whenNotPaused {
    require(_amount <= checkClientFund(msg.sender), "Amount exceeds your deposit");
```

The checkClientFund will revert because it will check if the caller is whitelisted. Even worse case is if a malicious owner decides to remove clients from the whitelist and leaving them without a chance to withdraw their money.

## Recommendation
SupraVRF_audit-1.md Call withdrawFundClient inside the removeClientFromWhitelist function so the clients are returned any left money in their balance.

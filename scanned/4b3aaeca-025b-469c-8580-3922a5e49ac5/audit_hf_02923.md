# [H] MaliciousUserCanMintUnlimitedAmountofNFTsDuetoReentrancy in whitelistMint() and FCFSMint()

## Summary
Severity: High
Contest weight: 0.5373
Dataset id: 16260
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
// whitelistMint() and FCFSMint() are vulnerable to reentrancy
```
The whitelistMint() and FCFSMint() functions are vulnerable to reentrancy. We can see that the function fails to apply a reentrancy modifier. When a malicious user calls them, they can do a reentrancy attack via the _safeMint() function that is called. We can see that absolutely all variables are updated afterwards. Thus, a malicious user can mint as many NFTs as he wants.

## Recommendation
Consider adding a reentrancy modifier on whitelistMint() and FCFSMint().

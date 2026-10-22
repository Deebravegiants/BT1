# [M] _manageIndexes() updates addressKeys and keyHolders for transfers where value = 0

## Summary
Severity: Medium
Contest weight: 0.5584
Dataset id: 10000
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can add themselves to addressKeys and keyHolders even if they do not hold the corresponding key, causing getKeysForHolder() and getHolders() to return incorrect values.

The _manageIndexes() function adds to addressKeys and keyHolders when the to address of a transfer is non-zero:
```solidity
if(address(0) != to) {
    addressKeys[to].add(id);
    keyHolders[id].add(to);
}
```
However, since the function does not check if value is non-zero, _manageIndexes() will still update both mappings for transfers with zero value.
This allows users to add themselves to both mappings for any arbitrary key ID by performing a self-transfer with zero value. For example, a user can call safeTransferFrom() with:
• from and to as their own address
• id as the key ID they want to add
• value = 0
After the transfer is performed, getKeysForHolder() will include the new key ID and getHolders() will include their address, even though they do not own a key with that ID.

## Recommendation
Only update addressKeys and keyHolders if value is non-zero:
```solidity
- if(address(0) != to) {
+ if (address(0) != to && value != 0) {
    addressKeys[to].add(id);
    keyHolders[id].add(to);
}
```

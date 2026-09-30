# [H] Soulbound checks and _manageIndexes() can be bypassed by specifying duplicate key IDs in ids

## Summary
Severity: High
Contest weight: 0.8892
Dataset id: 9997
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users who have more keys for a certain key ID than soulboundKeyAmounts can transfer all their keys to another address. Additionally, addressKeys and keyHolders will contain key IDs and addresses respectively that should have been removed after a transfer.

The _update() function enforces soulbound checks for users by ensuring that the remaining balance after the transfer is not less than soulboundKeyAmounts for each ID in ids:
```solidity
for(uint256 x = 0; x < ids.length; x++) {
    // we need to allow address zero during minting,
    // and we need to allow the locksmith to violate during burning
    if ( (from != address(0)) && (to != address(0)) && (balanceOf(from, ids[x]) - values[x]) < soulboundKeyAmounts[from][ids[x]]) {
        revert SoulboundTransferBreach();
    }
```
However, this check can be bypassed by specifying duplicate key IDs in ids. For example:
• Alice has two keys of id = 1.
• soulboundKeyAmounts[alice][1] = 1, which means that one of Alice's keys should not be transferable.
• Alice calls safeBatchTransferFrom() with:
– ids = [1, 1]
– values = [1, 1]
– The check above passes as balanceOf(alice, ids[x]) - values[x] = 1 for all x in ids.
– Therefore, both of Alice's keys are transferred to another address.
Similarly, _manageIndexes() removes from addressKeys and keyHolders under the following condition:
```solidity
// lets keep track of each key that is moving
if(balanceOf(from, id) == value) {
    addressKeys[from].remove(id);
    keyHolders[id].remove(from);
}
```
However, if ids contains duplicate key IDs as shown in the example above, balanceOf() will not be equal to value. Therefore, addressKeys and keyHolders will not be updated even when the user has transferred all his keys.

## Recommendation
In _update(), consider ensuring that ids does not contain duplicate key IDs:
```solidity
for(uint256 x = 0; x < ids.length; x++) {
    for (uint256 y = 0; y < x; y++) {
        if (ids[x] == ids[y]) {
            revert DuplicateKeyID();
        }
    }
    // we need to allow address zero during minting,
    // and we need to allow the locksmith to violate during burning
    if ( (from != address(0)) && (to != address(0)) && (balanceOf(from, ids[x]) - values[x]) < soulboundKeyAmounts[from][ids[x]]) {
        revert SoulboundTransferBreach();
    }
```

# [H] _removeStackPosition() always reverts

## Summary
Severity: High
Contest weight: 0.7315
Dataset id: 3211
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
removeStackPosition() always reverts since it calls stack array for an index beyond its length:  
```solidity
for (i; i < length; ) {
    unchecked {
        newStack[i] = stack[i + 1];
        ++i;
    }
}
```
Notice that for i==length-1, stack[length] is called. This reverts since length is the length of stack array. Additionally, the intention is to delete the element from stack at index position and shift left the elements appearing after this index. However, an addition increment to the loop index i results in newStack[position] being empty, and the shift of other elements doesn't happen.

## Recommendation
Apply this diff to LienToken.sol#L823-L831:
```solidity
for (i; i < length - 1; ) {
    unchecked {
        newStack[i] = stack[i + 1];
        ++i;
    }
}
```

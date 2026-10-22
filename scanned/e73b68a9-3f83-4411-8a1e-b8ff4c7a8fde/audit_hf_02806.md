# [M] Updating protocolFeeTo

## Summary
Severity: Medium
Contest weight: 0.3858
Dataset id: 15275
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SofamonWearable has the following functions to update the fee receiver.
```solidity
function updateRoyaltyFeeTo() public {
    royaltyFeeTo = ISofamonWearableFactory(machine).protocolFeeTo();
    emit NewRoyaltyFeeTo(royaltyFeeTo);
}
```
So, royaltyFeeTo should always be updated manually. Some bad scenarios are possible:
1. By default it is set to address(0) if the function was never called => royalties sent to zero address
2. machine can be updated => royalties sent to the deprecated address
3. protocolFeeTo can be updated in machine => royalties sent to the old protocolFeeTo address

## Recommendation
Consider reading ISofamonWearableFactory(machine).protocolFeeTo() always, not storing the address on SofamonWearable. updateRoyaltyFeeTo() can be removed.

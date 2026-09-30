# [C] Several issues in adding player to raffle list

## Summary
Severity: Critical
Contest weight: 0.3793
Dataset id: 16270
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Varonve.md makes the gas cost higher the more people join the raffle. The more players join, the higher the gas cost. Eventually gas costs could become so expensive that they could not fit in a single block, or too expensive for users, leading to DoS. Adding element to a storage array like this would not work and revert - this is not possible because the index is not instantiated because storage arrays are not fixed size. Only existing elements can be set like this in for storage arrays.
```solidity
for (uint256 i = 0; i < list.length; i++) {
    if (list[i] == _address) {
        break;
    } else {
        list[list.length] = _address;
    }
}
```
Another problem is that the user would be added to the list multiple times since when the loop iterates if the _address is not at index it would add it on the iteration. For example if the list has 50 addresses and the current is brand new it would add it 50 times.

## Recommendation
```solidity
// raffle and if he has do not add him in the joinedAddresses[raffleId] list again. This would fix the
revert AlreadyJoined();
if (joinedRaffle[id][_address]) revert AlreadyJoined();
// - for (uint256 i = 0; i < list.length; i++) {
// - if (list[i] == _address) {
// - break;
// - } else {
// - list[list.length] = _address;
list.push(_address);
joinedRaffle[id][_address] = true;
Varonve.md
```

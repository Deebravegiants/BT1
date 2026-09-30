# [H] Group numCatalyst Counter Decrement Issue

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23325
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Removing an individual from a group does not properly decrement the `groups.numCatalyst` to track the number of catalysts on that group.

When removing an individual from a group, the `group.numCatalyst` counter only checks if the individual's `numCatalyst` is != 0; if so, it decrements `group.numCatalyst` by 1, regardless of how many entities the individual is a catalyst for. Each individual can be a catalyst on multiple entities, and each time the individual is set as the catalyst on an entity, both the individual and the group `numCatalyst` grow.

```solidity
//FiveFiftyRule.sol//
27
function createEntity(
...
) external restricted {
...
uint16 gid = individualData[catalyst].groupId;
//@audit-info => The same catalyst increments the numCatalyst counter on the group each time it's added
as a catalyst on a != entity!,!
@> if (gid != 0) ++groups[gid].numCatalyst;
...
}
function removeIndividual(uint16 id, address individual) external restricted {
...
GroupData storage gData = groups[id];
//@audit-issue => Decrements the group numCatalysts only by one, regardless of how many times the
individual is a catalyst on != entities,!
@> if (iData.numCatalyst != 0) --gData.numCatalyst;
...
}
```

The group `numCatalyst` increments each time an individual is set as a catalyst on an entity, but when the individual is removed from the group, `group.numCatalyst` decrements by one, regardless of how many times it was incremented because of the individual being assigned as a catalyst on multiple entities.

Impact: `groups.numCatalyst` can be incorrect and fail to accurately track the actual number of catalysts among all entities where individuals are registered as catalysts. This can cause the execution path in the `FiveFiftyRule::canTransfer` function to follow the wrong path and, subsequently, make incorrect updates to the accounting.

## Proof of Concept
```solidity
function test_numCatalystInGroupsPoC() public {
// create group with one member
address u = getDomesticUser(0);
address u2 = getDomesticUser(1);
address[] memory inds = new address[](2);
inds[0] = u;
inds[1] = u2;
uint16 gid = 10;
address entityA = makeAddr("entityA");
address entityB = makeAddr("entityB");
fiveFiftyProxy.createGroup(gid, inds);
//@audit => Create two entities where individual `u` is the catalyst
fiveFiftyProxy.createEntity(entityA, u, 100, 100, inds);
fiveFiftyProxy.createEntity(entityB, u, 100, 100, inds);
assertEq(fiveFiftyProxy.getGroupNumCatalyst(gid), 2);
//@audit => Remove the only user of the group who is a numCatalyst on entities
fiveFiftyProxy.removeIndividual(gid, u);
28
//@audit-issue => The numCatalyst is left as 1 even though any of the remaining individuals in
the group is a catalyst on an entity,!
assertEq(fiveFiftyProxy.getGroupNumCatalyst(gid), 1);
}
```

## Recommendation
Consider refactoring the accounting to track the `group.numCatalyst` correctly, ensuring it is updated when removing and adding individuals to a group, as well as when setting an individual as a catalyst of an entity. Ensure there is a symmetric relation among these operations.

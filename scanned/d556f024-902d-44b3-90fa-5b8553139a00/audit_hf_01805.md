# [M] KeyLocker.redeemKeys() can get permanently bricked

## Summary
Severity: Medium
Contest weight: 0.5953
Dataset id: 9999
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
KeyLocker.redeemKeys() will permanently revert when the Locksmith's minted keys reach a certain value.

The redeemKeys function is designed to redeem keys left in the locker. An issue arises from the inspectKey call within this function.
```solidity
function redeemKeys(address locksmith, uint256 rootKeyId, uint256 keyId, uint256 amount) external {
    ILocksmith l = ILocksmith(locksmith);
    // can't redeem zero
    if(amount < 1) {
        revert InvalidInput();
    }
    // make sure the key used is actually a root key
```
The problem lies in the Locksmith.inspectKey call, where an attempt is made to figure out the keys associated with the ring by invoking EnumerableSet.values(). 
```solidity
function inspectKey(uint256 keyId) public view returns (bool, bytes32, uint256, bool, uint256[] memory) {
    uint256[] memory empty = new uint256[](0);
    // the key is a valid key number
    return ((keyId < keyCount),
        // the human readable name of the key
        keyData[keyId].name,
        // ring Id of the key
        keyRingAssociations[keyId],
        // the key is a root key
        _isRootKey(keyId),
        // the keys associated with the ring
        keyId >= keyCount ? empty : ringRegistry[keyRingAssociations[keyId]].keys.values());
}
```
As shown in OZ's documentation, this might be a problem:
* WARNING: This operation will copy the entire storage to memory, which can be quite expensive. This is designed
* to mostly be used by view accessors that are queried without any gas fees. Developers should keep in mind that
* this function has an unbounded cost, and using it as part of a state-changing function may render the function
* uncallable if the set grows to a point where copying to memory consumes too much gas to fit in a block.
*/
function values(UintSet storage set) internal view returns (uint256[] memory) {
Even though inspectKey is a view function, redeemKeys is state-changing. Then, because keys are not removed from the set when burned, we can assume that the set will always increase. As a result, when the data gets to a point where its too big, any keys in KeyLocker.sol will be forever locked.

## Recommendation
Given that only two return values from inspectKeys are used by redeemKeys, the easiest thing to do is expose a getter function from Locksmith that would allow the fetching of the root ring that needs to be used later and use it and isRootKey instead.
### Locksmith.sol
```solidity
function getRootRingId(uint256 keyId) public view returns (uint256) {
    return keyRingAssociations[keyId];
}
```
### Keylocker.sol
```solidity
function redeemKeys(address locksmith, uint256 rootKeyId, uint256 keyId, uint256 amount) external {
    (,,uint256 rootRing,bool isValidRoot,) = l.inspectKey(rootKeyId);
    uint256 rootRing = l.getRootRingId(rootKeyId);
    uint256 isValidRoot = l.isRootKey(rootKeyId)
```

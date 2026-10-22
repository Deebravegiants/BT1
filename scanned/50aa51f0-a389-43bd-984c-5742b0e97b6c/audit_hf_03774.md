# [M] updateCommitmentBorrowers does not delete

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 19952
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Delete a complex structure that includes a mapping will cause a problem. See [ethereum/solidity#11843](https://github.com/ethereum/solidity/pull/11843) for more info.
The lender can update the list of borrowers by calling LenderCommitmentForwarder.updateCommitmentBorrowers. The list of borrowers is EnumerableSetUpgradeable.AddressSet that is a complex structure containing a mapping. Using the delete keyword to delete this structure will not erase the mapping inside it. Let's look at the code of this function.
```solidity
mapping(uint256 => EnumerableSetUpgradeable.AddressSet)
    internal commitmentBorrowersList;

function updateCommitmentBorrowers(
    uint256 _commitmentId,
    address[] calldata _borrowerAddressList
) public commitmentLender(_commitmentId) {
    delete commitmentBorrowersList[_commitmentId];
    _addBorrowersToCommitmentAllowlist(_commitmentId, _borrowerAddressList);
}
```
I wrote a similar function to prove the problem.
```solidity
using EnumerableSet for EnumerableSet.AddressSet;
mapping(uint256 => EnumerableSet.AddressSet) internal users;

function test_deleteEnumerableSet() public {
    uint256 id = 1;
    address[] memory newUsers = new address[](2);
    newUsers[0] = address(0x1);
    newUsers[1] = address(0x2);
    for (uint256 i = 0; i < newUsers.length; i++) {
        users[id].add(newUsers[i]);
    }
    delete users[id];
    newUsers[0] = address(0x3);
    newUsers[1] = address(0x4);
    for (uint256 i = 0; i < newUsers.length; i++) {
        users[id].add(newUsers[i]);
    }
    bool exist = users[id].contains(address(0x1));
    if(exist) {
        emit log_string("address(0x1) exist");
    }
    exist = users[id].contains(address(0x2));
    if(exist) {
        emit log_string("address(0x2) exist");
    }
}
/*
[PASS] test_deleteEnumerableSet() (gas: 174783)
Logs:
address(0x1) exist
address(0x2) exist
*/
```
The deleted users can still successfully call LenderCommitmentForwarder.acceptCommitment to get a loan.

## Recommendation
In order to clean an EnumerableSet, you can either remove all elements one by one or create a fresh instance using an array of EnumerableSet.

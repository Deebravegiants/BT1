# [M] Storage operations optimization

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

There are a lot of operations that write some value to the storage (uses `SSTORE` opcode) without actually changing it. 

#### Examples

In `getAndUpdateValue ` function of `DelegationController` and `TokenLaunchLocker`:


**new_code/contracts/delegation/DelegationController.sol:L711-L715**
```solidity
for (uint i = sequence.firstUnprocessedMonth; i <= month; ++i) {
    sequence.value = sequence.value.add(sequence.addDiff[i]).sub(sequence.subtractDiff[i]);
    delete sequence.addDiff[i];
    delete sequence.subtractDiff[i];
}
```

In `handleSlash` function of `Punisher` contract `amount` will be zero in most cases:


**new_code/contracts/delegation/Punisher.sol:L66-L68**
```solidity
function handleSlash(address holder, uint amount) external allow("DelegationController") {
    _locked[holder] = _locked[holder].add(amount);
}
```

#### Recommendation

Check if the value is the same and don't write it to the storage in that case.

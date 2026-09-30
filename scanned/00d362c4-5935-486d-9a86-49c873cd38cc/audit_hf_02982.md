# [M] FraxlendPair#setTimeLock: Allows the owner to reset TIME _LOCK_ ADDRESS

## Summary
Severity: Medium
Contest weight: 0.3895
Dataset id: 16610
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Allows to reset **TIME _LOCK_ ADDRESS** value multiple times by the owner. According to comments in FraxlendPairCore this should act as a constant/immutable value. Given that this value will be defined through function **setTimeLock** in **FraxLendPair** contract this value can be changed whenever the owner wants. This does not seem to be the expected behaviour.

## Proof of Concept
The owner can call the function **setTimeLock** whenever they want, which resets the value of **TIME _LOCK_ ADDRESS**.

## Recommendation
Add a bool which act as mutex if **TIME _LOCK_ ADDRESS** has already been set, and modify **setTimeLock** function in FraxlendPair contract

```solidity
// In FraxlendPair contract
bool public timelockSetted;
function setTimeLock(address _newAddress) external onlyOwner {
    require(!timelockSetted);
    emit SetTimeLock(TIME_LOCK_ADDRESS, _newAddress);
    TIME_LOCK_ADDRESS = _newAddress;
    timelockSetted = true;
}
```

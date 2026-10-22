# [H] OperatorRewardsCollector Missing Call To OZ _disableInitializers

## Summary
Severity: High
Contest weight: 0.5505
Dataset id: 14557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following passage can be found in the OpenZeppelin documentation for writing upgradable contracts.
Do not leave an implementation contract uninitialized.
An uninitialized implementation contract can be taken over by an attacker, which may impact the proxy.
To prevent the implementation contract from being used, you should invoke the _disableInitializers function in the constructor to automatically lock it when it is deployed
```solidity
/// @custom:oz-upgrades-unsafe-allow constructor
constructor() {
    _disableInitializers();
}
```
OperatorRewardsCollector is missing a constructor which calls _disableInitializers().

## Recommendation
Add a constructor which invokes _disableInitializers() as described in the OZ documentation.

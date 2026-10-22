# [M] AMM Cannot Be `initialize`

## Summary
Severity: Medium
Contest weight: 0.5762
Dataset id: 1625
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract `AMM.sol` cannot be initialize unless it is called from the `_governance` address.

This prevents the use of a deployer account and requires the governance to be able to deploy proxy contracts and encode the required arguments. If this is not feasible then the contract cannot be deployed.

## Proof of Concept
`initialize()` calls `_setGovernace(_governance);` which will store the governance address.

Following this it will call `syncDeps(_registry);` which has `onlyGovernance` modifier. Thus, if the `msg.sender` of `initialize()` is not the same as the parameter `_governance` then the initialisation will revert.
    
```solidity
function initialize(
    address _registry,
    address _underlyingAsset,
    string memory _name,
    address _vamm,
    address _governance
) external initializer {
    _setGovernace(_governance);

    vamm = IVAMM(_vamm);
    underlyingAsset = _underlyingAsset;
    name = _name;
    fundingBufferPeriod = 15 minutes;

    syncDeps(_registry);
}
```

## Recommendation
Consider adding the steps manually to `initialize()`. i.e.
    
```solidity
function initialize(
    address _registry,
    address _underlyingAsset,
    string memory _name,
    address _vamm,
    address _governance
) external initializer {
    _setGovernace(_governance);

    vamm = IVAMM(_vamm);
    underlyingAsset = _underlyingAsset;
    name = _name;
    fundingBufferPeriod = 15 minutes;

    IRegistry registry = IRegistry(_registry);
    clearingHouse = registry.clearingHouse();
    oracle = IOracle(registry.oracle());
}
```

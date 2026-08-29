# [M] [NAZ-M2] Unchecked return of `execute()` 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-01-popcorn
Published: 2023-02-07
Source: https://github.com/code-423n4/2023-01-popcorn-findings/issues/541
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-popcorn//blob/main/src/vault/VaultController.sol#L238


# Vulnerability details

## Impact
Across the `VaultController.sol` there are many external calls to the `AdminProxy.sol` via `execute()`. Looking at the `execute()` function in `AdminProxy.sol`:
```solidity
function execute(address target, bytes calldata callData)
    external
    onlyOwner 
    returns (bool success, bytes memory returndata) 
{
    return target.call(callData);
}
```
As one can see it does a call to the target contract with the provided `callData`. Going back to the `VaultController.sol` the success of the call is check and reverts if unsuccessful. However, in one instance this check is missed and could cause issues.

## Proof of Concept
Looking at that specific instance:
```solidity
function __deployAdapter(
    DeploymentArgs memory adapterData,
    bytes memory baseAdapterData,
    IDeploymentController _deploymentController
  ) internal returns (address adapter) {
    (bool success, bytes memory returnData) = adminProxy.execute(
      address(_deploymentController),
      abi.encodeWithSelector(DEPLOY_SIG, ADAPTER, adapterData.id, _encodeAdapterData(adapterData, baseAdapterData))
    );
    if (!success) revert UnderlyingError(returnData);

    adapter = abi.decode(returnData, (address));

    adminProxy.execute(adapter, abi.encodeWithSelector(IAdapter.setPerformanceFee.selector, performanceFee));//@audit unchecked like the others are
}
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-popcorn-findings/issues/541_

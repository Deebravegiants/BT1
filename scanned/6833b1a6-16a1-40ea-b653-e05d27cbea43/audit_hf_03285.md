# [M] Unchecked return of `execute`

## Summary
Severity: Medium
Contest weight: 0.5900
Dataset id: 18032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
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

It is clear that the last call to `AdminProxy.sol`’s `execute` is not checked.

## Recommendation
Consider adding a check similar to how it is done in the rest of the contract.

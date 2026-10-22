# [M] `VaultController`

## Summary
Severity: Medium
Contest weight: 0.7219
Dataset id: 18029
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the VaultController contract’s upgrade path for the DeploymentController component. The intended design is that when the owner calls setDeploymentController to replace the current DeploymentController with a new implementation, the old DeploymentController must first nominate the new address as the owner of its dependent contracts – cloneFactory, cloneRegistry and templateRegistry – by invoking nominateNewDependencyOwner. The new DeploymentController then calls acceptDependencyOwnership to complete the transfer. In the existing code, setDeploymentController only updates the internal pointer to the new DeploymentController and emits an event; it never calls the old DeploymentController’s nominateNewDependencyOwner function through the AdminProxy, nor does it trigger acceptDependencyOwnership on the new controller. Consequently, the dependent contracts remain owned by the previous DeploymentController, which may be abandoned or compromised. This breaks the protocol’s upgradeability: after the apparent switch, the new DeploymentController cannot manage clones or templates, leading to denial‑of‑service conditions where users cannot create new vaults, retrieve templates, or interact with existing clones. From a user’s perspective the UI may show that the deployment controller has changed, but actions that rely on the cloneFactory or registry silently fail, resulting in missing balances or failed operations without clear error messages. The issue was discovered during a Code4rena audit by comparing the documented upgrade flow with the actual implementation and noticing the missing call. It is subtle because the function does not revert and the event suggests success, making the failure hard to detect without deeper testing. The root cause is a missing cross‑contract call that should transfer ownership of dependency contracts before the pointer is updated. To remediate, setDeploymentController must first invoke the old DeploymentController’s nominateNewDependencyOwner via the AdminProxy, then call acceptDependencyOwnership on the new DeploymentController, and only after these steps update the internal storage and emit the change event. This ensures that ownership of all dependent contracts is correctly transferred and the protocol’s upgrade mechanism functions as intended.

## Proof of Concept
The current protocol supports the replacement of the new DeploymentController, which can be switched by `VaultController.setDeploymentController()`.

Normally, when switching, the owner of the cloneFactory/cloneRegistry/templateRegistry in the old DeploymentController should also be switched to the new DeploymentController.

DeploymentController’s `nominateNewDependencyOwner()` implementation is as follows:
    
```solidity
  /**
   * @notice Nominates a new owner for dependency contracts. Caller must be owner. (`VaultController` via `AdminProxy`)
   * @param _owner The new `DeploymentController` implementation
   */
  function nominateNewDependencyOwner(address _owner) external onlyOwner {
    IOwned(address(cloneFactory)).nominateNewOwner(_owner);
    IOwned(address(cloneRegistry)).nominateNewOwner(_owner);
    IOwned(address(templateRegistry)).nominateNewOwner(_owner);
  }
```

But there is a problem here, VaultConttroler.sol does not implement the code to call old_Deployerment.

`nominateNewDependencyOwner()`, resulting in DeploymentController can not switch properly, `nominateNewDependencyOwner()`’s Remarks: `Caller must be owner. (`VaultController` via `AdminProxy`)`

But in fact the VaultController does not have any code to call the nominateNewDependencyOwner:
    
```solidity
  function setDeploymentController(IDeploymentController _deploymentController) external onlyOwner {
    _setDeploymentController(_deploymentController);
  }

  function _setDeploymentController(IDeploymentController _deploymentController) internal {
    if (address(_deploymentController) == address(0) || address(deploymentController) == address(_deploymentController))
      revert InvalidDeploymentController(address(_deploymentController));

    emit DeploymentControllerChanged(address(deploymentController), address(_deploymentController));

    deploymentController = _deploymentController;
    cloneRegistry = _deploymentController.cloneRegistry();
    templateRegistry = _deploymentController.templateRegistry();
  }
```

## Recommendation
`setDeploymentController()` need call `nominateNewDependencyOwner()`:
    
```solidity
contract VaultController is Owned {
  function setDeploymentController(IDeploymentController _deploymentController) external onlyOwner {
    
    //1. old deploymentController nominateNewDependencyOwner
    (bool success, bytes memory returnData) = adminProxy.execute(
       address(deploymentController),
       abi.encodeWithSelector(
         IDeploymentController.nominateNewDependencyOwner.selector,
         _deploymentController
       )
     );
     if (!success) revert UnderlyingError(returnData); 
     
     //2. new deploymentController acceptDependencyOwnership
     _deploymentController.acceptDependencyOwnership(); 
    
     _setDeploymentController(_deploymentController);        
  }
}
```

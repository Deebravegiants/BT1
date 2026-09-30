# [M] Impossible to execute whitelisted actions and

## Summary
Severity: Medium
Contest weight: 0.5901
Dataset id: 22604
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Impossible to execute whitelisted actions that require sending the native token. The LiquidityWarehouse.execute() function internally calls the LiquidityWarehouseAccessControl._execute() which is on charge to allow the execution of whitelisted actions. The problem is that the external call is capable of sending the native token, but the LiquidityWarehouse.execute() function is not a payable function. So, the only means the contract could have to receive the native token to send it to the target contract would be by receiving the native within the same call to the LiquidityWarehouse.execute() function, or in other words, if the external call to the target required to send native, the only way that native could be send to the target would be by sending it as part of the call to the LiquidityWarehouse.execute() function. But, because the LiquidityWarehouse.execute() function is not a payable function, if the executeActions.value != 0, the whole execution will revert because the LiquidityWarehouse won't have any native to send to the target contract.
```solidity
function execute(LiquidityWarehouseAccessControl.ExecuteAction[] calldata executeActions)
    external
    override
    nonReentrant
{
    // allow the senders to send native when calling it!
    _execute(executeActions, msg.sender == owner());
}

function _execute(ExecuteAction[] calldata executeActions, bool isOwner) internal {
    for (uint256 i; i < executeActions.length; ++i) {
        ...
        // because the contract has no native tokens to send to the target!
        (bool success,) = executeAction.target.call{value: executeAction.value}(executeAction.data);
        if (!success) revert ExecutionFailed(executeAction.target, msg.sender, fnSelector);
    }
}
```
Impossible to execute whitelisted actions that require sending the native token.

## Recommendation
Make payable the LiquidityWarehouse.execute() function.
```solidity
function execute(LiquidityWarehouseAccessControl.ExecuteAction[] calldata executeActions)
    external
    payable
    override
    nonReentrant
{
    _execute(executeActions, msg.sender == owner());
}
```

# [M] Timelock on emergencyUninstallHook() can be bypassed

## Summary
Severity: Medium
Contest weight: 0.4469
Dataset id: 3908
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function emergencyUninstallHook(address hook, bytes calldata deInitData) external payable
    onlyEntryPoint {
    AccountStorage storage accountStorage = _getAccountStorage();
    uint256 hookTimelock = accountStorage.emergencyUninstallTimelock[hook];
    if (hookTimelock == 0) {
        // if the timelock hasnt been initiated, initiate it
        accountStorage.emergencyUninstallTimelock[hook] = block.timestamp;
        emit EmergencyHookUninstallRequest(hook, block.timestamp);
    } else if (block.timestamp >= hookTimelock + 3 * _EMERGENCY_TIMELOCK) {
        // if the timelock has been left for too long, reset it
        accountStorage.emergencyUninstallTimelock[hook] = block.timestamp;
        emit EmergencyHookUninstallRequest(hook, block.timestamp);
    } else if (block.timestamp >= hookTimelock + _EMERGENCY_TIMELOCK) {
        // if the timelock expired, clear it and uninstall the hook
        accountStorage.emergencyUninstallTimelock[hook] = 0;
        _uninstallHook(hook, deInitData);
        emit ModuleUninstalled(MODULE_TYPE_HOOK, hook);
    } else {
        // if the timelock is initiated but not expired, revert
        revert EmergencyTimeLockNotExpired();
    }
}
```
This allows the timelock to be bypassed through the following steps:
• Call emergencyUninstallHook() to place an uninstall request even before installing the hook (this records a timestamp corresponding to the hook address).
• After nearly a day has passed, install the hook and use it.
• Immediately call emergencyUninstallHook() to utilize the request that was placed before.
• As only a day has passed, the call will go through.
• The timelock has been effectively bypassed by the account.

## Recommendation
UninstallModule() on Nexus.sol checks that the module they are trying to uninstall through the call is actually installed. Add the same check to emergencyUninstallHook().

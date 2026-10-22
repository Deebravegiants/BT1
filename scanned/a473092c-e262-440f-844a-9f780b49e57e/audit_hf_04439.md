# [M] Potential stale data in `FundFlowController::performUpkeep` can lead to incorrect state updates

## Summary
Severity: Medium
Contest weight: 0.4539
Dataset id: 21930
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** The `FundFlowController::checkUpkeep` function calculates `nextGroupOpVaultsTotalUnbonded` and `nextGroupComVaultsTotalUnbonded` by iterating over vaults and checking their `unbondingActive` status. This data is then encoded and passed to `performUpkeep` by keepers.

However, there's a potential time delay between `checkUpkeep` and `performUpkeep` execution, which could lead to stale data being used to update the system state. The `unbondingActive` status of vaults is time-sensitive, based on the current block timestamp and each vault's claim period end time. If the `performUpkeep` transaction is delayed due to network congestion or other factors, the `totalUnbonded` values used for updates may no longer accurately reflect the current state of the vaults.

`FundFlowController.sol`
```solidity
function checkUpkeep(bytes calldata) external view returns (bool, bytes memory) {
    // ... (other code)
    (
        uint256[] memory curGroupOpVaultsToUnbond,
        uint256 nextGroupOpVaultsTotalUnbonded
    ) = _getVaultUpdateData(operatorVCS, nextUnbondedVaultGroup);
    // ... (similar for community vaults)
    return (
        true,
        abi.encode(
            curGroupOpVaultsToUnbond,
            nextGroupOpVaultsTotalUnbonded,
            curGroupComVaultsToUnbond,
            nextGroupComVaultsTotalUnbonded
        )
    );
}

function performUpkeep(bytes calldata _data) external {
    // ... (decoding and using potentially stale data)
}
```
** The use of stale data in performUpkeep can lead to incorrect state updates. The system may allow more or fewer unbondings than it should, leading to discrepancies between the recorded state and the actual state of the vaults. In a worst-case scenario, funds that should be unbonded might remain locked, or funds that should still be locked might be prematurely released.

## Recommendation
** Consider modifying `performUpkeep` to recalculate the `totalUnbonded` values at the time of execution, rather than relying on potentially stale data from checkUpkeep.

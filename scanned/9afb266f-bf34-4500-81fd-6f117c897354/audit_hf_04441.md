# [H] Incorrect Handling of Deposit Data in FundFlowController

## Summary
Severity: High
Contest weight: 0.7923
Dataset id: 21932
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** The `getDepositData` function in the `FundFlowController` contract incorrectly handles the case when operator vaults can accommodate all deposits. This leads to empty deposit data being passed to operator vaults, potentially causing deposits to fail or be misallocated.

Relevant code snippet from `FundFlowController`:
```solidity
function getDepositData(uint256 _toDeposit) external view returns (bytes[] memory) {
    uint256 toDeposit = 2 * _toDeposit;
    bytes[] memory depositData = new bytes[](2);

    (
        uint64[] memory opVaultDepositOrder,
        uint256 opVaultsTotalToDeposit
    ) = _getVaultDepositOrder(operatorVCS, toDeposit);
    depositData[0] = abi.encode(opVaultDepositOrder);

    if (opVaultsTotalToDeposit < toDeposit) {
        (uint64[] memory comVaultDepositOrder, ) = _getVaultDepositOrder(
            communityVCS,
            toDeposit - opVaultsTotalToDeposit
        );
        depositData[1] = abi.encode(comVaultDepositOrder);
    } else {
        depositData[0] = abi.encode(new uint64[](0)); // @audit: Should be depositData[1]
    }

    return depositData;
}
```

Note that the depositData[0] that contains the vault ID order is deleted when operator vaults can handle full deposit. This treatment is also inconsistent with the `getWithdrawalData` function that correctly encodes only `withdrawalData[0]` in both the `if-else` logic flow.
```solidity
function getWithdrawalData(uint256 _toWithdraw) external view returns (bytes[] memory) {
    uint256 toWithdraw = 2 * _toWithdraw;
    bytes[] memory withdrawalData = new bytes[](2);

    (
        uint64[] memory comVaultWithdrawalOrder,
        uint256 comVaultsTotalToWithdraw
    ) = _getVaultWithdrawalOrder(communityVCS, toWithdraw);
    withdrawalData[1] = abi.encode(comVaultWithdrawalOrder);

    if (comVaultsTotalToWithdraw < toWithdraw) {
        (uint64[] memory opVaultWithdrawalOrder, ) = _getVaultWithdrawalOrder(
            operatorVCS,
            toWithdraw - comVaultsTotalToWithdraw
        );
        withdrawalData[0] = abi.encode(opVaultWithdrawalOrder);
    } else {
        withdrawalData[0] = abi.encode(new uint64[](0)); //@audit correctly encoding this instead of withdrawalData[1]
    }

    return withdrawalData;
}
```

** `getDepositData` is called by the `PPKeeper` contract to compute the vaultId's that are passed to the priority pool to deposit queued tokens. This bug can cause deposits to fail or be misallocated when operator vaults have sufficient capacity to handle all deposits.

## Recommendation
** Consider modifying the `getDepositData` function to correctly handle the case when operator vaults can accommodate all deposits. The corrected code should be:
```diff
if (opVaultsTotalToDeposit < toDeposit) {
    (uint64[] memory comVaultDepositOrder, ) = _getVaultDepositOrder(
        communityVCS,
        toDeposit - opVaultsTotalToDeposit
    );
    depositData[1] = abi.encode(comVaultDepositOrder);
} else {
-   depositData[0] = abi.encode(new uint64[](0));
+   depositData[1] = abi.encode(new uint64[](0));
}
```

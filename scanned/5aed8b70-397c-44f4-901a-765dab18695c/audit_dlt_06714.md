# [M] Old AmoManager retains token allowance after replacement in `setAmoManager`

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/37
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/dod4ufn)

  **Beneficiary:** 0xf8e45a12a45CfBa70a24c00BC3492Ab948f028EE
  **Submission hash (on-chain):** 0x2a8b8160c607b6d1a164dc3fee8ed57f43e26639c5cc9bb3bb725d03693917b5
  **Severity:** medium
  
  **Description:**
  **Description**\
In the `AmoVault` contract, the `setAmoManager` function sets a new AmoManager and grants it an unlimited approval to spend the `dstable` token via the `approveAmoManager()` function. However, the function does **not** revoke the allowance granted to the previous AmoManager. As a result, even after a new AmoManager is set, the old AmoManager still retains full access to the vault's `dstable` balance.

This persistent approval is a security risk, particularly if the old AmoManager is compromised or becomes malicious, as it can still drain funds despite no longer being the designated manager.

**Attack Scenario**

1. Admin calls `setAmoManager(amoManager1)` to set the initial manager.
2. `approveAmoManager()` gives `amoManager1` unlimited allowance over `dstable`.
3. Later, the admin calls `setAmoManager(amoManager2)` to replace the manager.
4. `approveAmoManager()` grants unlimited allowance to `amoManager2`, but does **not** revoke `amoManager1`'s allowance.
5. `amoManager1` can still call `dstable.transferFrom()` and drain tokens from the vault.

**Recommendation**

```solidity
function setAmoManager(
    address _newAmoManager
) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_newAmoManager == address(0)) revert InvalidAmoManager();

    // Revoke approval from the previous AmoManager if set
    if (address(amoManager) != address(0)) {
        dstable.approve(address(amoManager), 0);
    }

    // Set new AMO manager
    amoManager = AmoManager(_newAmoManager); 

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/37_

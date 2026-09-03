# [M] Attacker can DOS the last user who wants to withdraw

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/127
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x591787555207a395813bc46276099d991761ec24e63901f0f508ee022876a254
  **Severity:** medium
  
  **Description:**
  **Description**\

The repay function checks a tolerance amount and reverts if the amount used to repay is greater than or less than the amount passed in. 
An attacker can weaponise this by repaying 2 wei directly on behalf of the contract. 
This amount is so small but it is enough to trigger a revert of the user's call to withdraw.


```solidity
    /**
     * @dev Repay debt to the lending pool, and make sure the output is as expected
     * @param token Address of the token
     * @param amount Amount of tokens to repay
     * @param onBehalfOf Address to repay on behalf of
     */
    function _repayDebtToPool(
        address token,
        uint256 amount,
        address onBehalfOf
    ) internal {
        // At this step, we assume that the funds from the depositor are already in the vault

        uint256 tokenBalanceBeforeRepay = ERC20(token).balanceOf(onBehalfOf);

        _repayDebtToPoolImplementation(token, amount, onBehalfOf);

        uint256 tokenBalanceAfterRepay = ERC20(token).balanceOf(onBehalfOf);

        // Ensure the balance actually decreased
        if (tokenBalanceAfterRepay >= tokenBalanceBeforeRepay) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/127_

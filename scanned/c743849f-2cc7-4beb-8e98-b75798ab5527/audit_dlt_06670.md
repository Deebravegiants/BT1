# [M] isBuyed function returns wrong remainingAmount values or buy function is incorrectly implemeted

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/31
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/dod4ufn)

  **Beneficiary:** 0xf8e45a12a45CfBa70a24c00BC3492Ab948f028EE
  **Submission hash (on-chain):** 0x1bfcc9d04f4e28d3b79f09f38a0854908411c0949d9d4e955096ed6e213ad88f
  **Severity:** medium
  
  **Description:**
  **Description**  
The `isBuyed` function returns an incorrect value for the remaining amount that can be bought by a user. Specifically, the function has hardcoded conditions that are not verified in the `buy` function. It assumes that when `buyCounter[_address] == 1`, the remaining amount is always `minBuy`, and when `buyCounter[_address] > 1`, the remaining amount is set to 0. However, the `buy` function does not enforce such checks and allows for an infinite remaining amount when the `buyCounter` is not checked adequately. This leads to discrepancies between the intended and actual remaining purchase limits, which can allow users to bypass limits and make more purchases than allowed.

**Attack Scenario**  
An attacker can exploit this vulnerability by calling the `isBuyed` function after a purchase, where the function would incorrectly return an infinite remaining amount for users who have bought once. This could allow them to bypass the constraints imposed in the `buy` function, especially if they manage to interact with the contract in ways that the function logic does not account for (such as making repeated purchases without the correct checks for `buyCounter`). The attacker could potentially keep exploiting this flaw, circumventing the intended limits on the purchase amounts.

**Attachments**


1. **Revised Code**  
```solidity
function isBuyed(address _address) external view returns (bool, uint256) {
    bool hasBought = buyCounter[_address] > 0;
    uint256 remainingAmount;
    if (_address == creator) {
        User storage user = userDetails[creator];
        remainingAmount = maxBuyCreator - user.buyAmount;
    } else {
        if (buyCounter[_address] == 0) {
            remainingAmount = maxBuyUser;
        } else if (buyCounter[_address] == 1) {
            remainingAmount = minBuy;  // Should check if this amount is still valid for the user
        } else {
            remainingAmount = 0;
        }
    }
    return (hasBought, remainingAmount);
}
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/31_

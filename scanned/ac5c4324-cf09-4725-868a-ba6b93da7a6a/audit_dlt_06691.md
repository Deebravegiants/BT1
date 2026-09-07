# [M] Possible Dos Of Withdraw Due To Grosss Amount For Net Calculation In `DStakeToken::previewWithdraw()`

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-27
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/273
Type: hats-finding

## Details
**Github username:** @OxTheAnzRider
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xtheanzrider)

  **Beneficiary:** 0xF78554Dfb77e2Da05BAeE87913CA9706eD40a027
  **Submission hash (on-chain):** 0x2c25aeb47be52c870cd674f110a1d400b501d50c7dc68b8f2d22b6149929c04d
  **Severity:** medium
  
  **Description:**
  **Description**

On withdraw the function follows a logic where it uses the asset amount as an input to call the `previewWithdraw()` to calculate the amount of share but then uses the share as an input calling the `convertToAssets()` to get the gross amount then does a check to ensure the gross amount is less or equal to the maxwithdraw of the user(owner)
```solidity
    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) public virtual override returns (uint256 shares) {
        shares = previewWithdraw(assets); // Calculate shares needed for net amount
        uint256 grossAssets = convertToAssets(shares); // Calculate gross amount from shares

        require(
            grossAssets <= maxWithdraw(owner),
            "ERC4626: withdraw more than max"
        );

        _withdraw(_msgSender(), receiver, owner, grossAssets, shares); // Pass GROSS amount to _withdraw
        return shares;
    }
```
the `previewWithdraw()` uses `_getGrossAmountRequiredForNet()` to get the the gross amount for net  then uses it to calculate the amount of of shares used for the gross amount calculation in the `withdraw()`. And if fee is set `_getGrossAmountRequiredForNet()` uses the formula
```solidity
        // grossAmount = netAmount / (1 - feeBps/ONE_HUNDRED_PERCENT_BPS)
        // grossAmount = netAmount * ONE_HUNDRED_PERCENT_BPS / (ONE_HUNDRED_PERCENT_BPS - feeBps)
        return
            (netAmount * BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
            (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS - withdrawalFeeBps_);
 ```   

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/273_

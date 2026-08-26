# [H] Share Pricing Ignores Debt Leading to Arbitrage Opportunities and Incorrect Vault Valuations

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-30
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/300
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xvd)

  **Beneficiary:** 0x23B5FbcF9dc2C5d5D6fDCd36d2239E6fC3aED2BA
  **Submission hash (on-chain):** 0xfbb59e2c5401f9f063ab97d0353ec975407da846aaa3e81531cbf16c20493d79
  **Severity:** high
  
  **Description:**
  **Description**\
The DLoopCoreBase.totalAssets() function contains a critical flaw where it only considers the vault's collateral position while completely ignoring the debt position when calculating total assets. 

In a leveraged vault system, the true economic value should be Total Collateral - Total Debt, but the current implementation only returns the collateral value. 

This creates a fundamental disconnect between the reported vault value and its actual economic worth.

The issue stems from the totalAssets() override in lines 624-634 of DLoopCoreBase.sol, where the function calls getTotalCollateralAndDebtOfUserInBase() but deliberately discards the debt component:

```Solidity
function totalAssets() public view virtual override returns (uint256) {
        // We override this function to return the total assets in the vault
        // with respect to the position in the lending pool
        // The dLend interest will be distributed to the dToken
        (uint256 totalCollateralBase, ) = getTotalCollateralAndDebtOfUserInBase(
            address(this)
        );
        // The price decimals is cancelled out in the division (as the amount and price are in the same unit)
        return
            convertFromBaseCurrencyToToken(
                totalCollateralBase,
                address(collateralToken)
            );
    }
```

Since all ERC4626 share pricing functions (convertToShares, previewDeposit, previewMint, etc.) depend on totalAssets(), this flaw propagates throughout the entire share pricing mechanism, leading to systematic overvaluation of vault shares when debt exists.

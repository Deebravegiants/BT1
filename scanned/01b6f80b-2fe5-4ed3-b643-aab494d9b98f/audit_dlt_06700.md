# [H] Attacker can manipulate the system to trigger Increase leverage and prevent users from ever withdrawing

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/119
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x0f74d6c2215c759ff2f7356e64263f81547b0c7f5c10047db8de44b0cd49d4f6
  **Severity:** high
  
  **Description:**
  **Description**\

The attacker can manipulate the Share to Asset calculation, which in turn affects the increase/ decrease leverage functions, permanent DOS and also DOS withdrawal for all other users. 

The total Asset function causes this issue. 

The total asset is obtained by calling the get user's details But this function calculates all the positional balances of a user.
While total debt can not be manipulated, Total Collateral can be. 

```solidity

 /**
     * @dev Override of totalAssets from ERC4626
     * @return uint256 Total assets in the vault
     */
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

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/119_

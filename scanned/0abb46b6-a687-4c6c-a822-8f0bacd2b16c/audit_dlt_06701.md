# [H] Attacker can break the entire contract by frontrunning with 1 wei.

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/113
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0xbad496a9c7f95925f500c2855b5932dbdee765805badea337acfee9adbf6a147
  **Severity:** high
  
  **Description:**
  **Description**\

Collateral token will be supplied to an Aave fork.  These tokens and other tokens to be borrowed will be supplied external users of which the dloop vault is technically a user too and also we borrow from there. 
An attacker can supply on behalf of this contract 1 or some few wei of a token by frontrunning the first deposit.
This donation will increase the total collateral base to 1 while the total debt remains at 0.

Because of the check in the get leverage call the entire contract will never function again, Hence, no one will be able to deposit into this vault ever.


```solidity
  function _depositToPoolImplementation(
        address caller,
        uint256 supplyAssetAmount // supply amount
    ) private returns (uint256) {
        // Transfer the assets to the vault (need the allowance before calling this function)
        collateralToken.safeTransferFrom(
            caller,
            address(this),
            supplyAssetAmount
        );

        // At this step, we assume that the funds from the depositor are already in the vault

        // Get current leverage before supplying (IMPORTANT: this is the leverage before supplying)

@audit>>         uint256 currentLeverageBpsBeforeSupply = getCurrentLeverageBps();

        // Make sure we have enough balance to supply before supplying
        uint256 currentCollateralTokenBalance = collateralToken.balanceOf(
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/113_

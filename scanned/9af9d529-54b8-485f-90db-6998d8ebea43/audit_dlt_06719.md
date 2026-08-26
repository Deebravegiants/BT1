# [M] There are a several unsafe `.approve` in several contracts

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/9
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/HEX)

  **Beneficiary:** 0x92e54e1279d674fde1E65aE028A29767a9D0dbC0
  **Submission hash (on-chain):** 0x5d4818cd9af7f557f398f510f9ab395daf4e58f14639e3765dd2fdb124da5ae9
  **Severity:** medium
  
  **Description:**
  ## Description

Some tokes do not behave like the eip20 dictates and when they did one they could revert and also these approves could return false

## Attack Scenario

For example in DStakeRouterDLend: 

```solidity
        IERC20(fromVaultAsset).approve(
            fromAdapterAddress,
            fromVaultAssetAmount
        );
```

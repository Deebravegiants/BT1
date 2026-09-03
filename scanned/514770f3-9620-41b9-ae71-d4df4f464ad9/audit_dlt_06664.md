# [M] Missing Validation for `firstBuyFee` Allows Creator to Bypass Buy Restrictions

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/64
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0x0bserver)

  **Beneficiary:** 0x88cBcd44a23Dc16dF47f144f6f6E111DB7433b71
  **Submission hash (on-chain):** 0x5deaae8baa0a5451e42246eaef3f66acae77b474762e4faad4580478d4055ed0
  **Severity:** medium
  
  **Description:**
  **Description:**\
The `MasterFastIDO` and `MasterNormalIDO` contracts have a `firstBuyFee` variable that is used to determine the initial buy fee on the token purchase for the creator. However, there is no validation of the `firstBuyFee` variable in the contract’s constructor, allowing the creator to bypass the minimum buy (`minBuyCreator`) and maximum creator buy (`maxBuyCreator`) restrictions that were intended to limit the creator’s buying behavior. This oversight enables the creator to potentially exceed these restrictions and perform actions that were meant to be prevented.

 **Impact:**
**Bypassing Restrictions:** The creator can bypass the minimum and maximum buy restrictions, allowing them to buy tokens at 0 price or raise more tokens than intended by the protocol.\
**Unfair Advantage:** This allows the creator to buy large amounts of tokens at favorable conditions, which could be exploited to manipulate the token’s price or the IDO process.\
**Loss of Fairness:** The protocol's fairness and integrity are compromised if the creator is able to exceed the predefined buying limits, potentially leading to trust issues among other participants in the IDO.\
**Market Manipulation Risk:** With the ability to bypass buy limits, the creator could have a disproportionate influence on the initial token distribution, leading to market manipulation.

**Fix:**\
To resolve this issue, add validation for the `firstBuyFee` variable in the constructor to ensure that the creator cannot bypass the buy restrictions. Specifically, the `firstBuyFee` should be checked against the `minBuyCreator` and `maxBuyCreator` variables to ensure the creator’s purchase remains within the intended limits:
```solidity
constructor() {
    // Validate firstBuyFee against min and max buy restrictions
++    require(firstBuyFee >= minBuyCreator, "First buy fee is less than minimum buy");
++    require(firstBuyFee <= maxBuyCreator, "First buy fee exceeds maximum buy");

    // Other constructor logic
}
```

# [H] Some users might get 0 shares for assets provided in DStakeToken contract

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-27
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/286
Type: hats-finding

## Details
**Github username:** @cpp-phoenix
  **Twitter username:** 0xrochimaru
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/aarambh_audits)

  **Beneficiary:** 0x06a314624FBc79CEb00619a9703F9D2068890b2b
  **Submission hash (on-chain):** 0x834aa860c1cf3db737174babc87746c498b36bf1086cadc69223a744c44af33c
  **Severity:** high
  
  **Description:**
  **Description**\
In contract `DStakeToken` withdrawal fee in charged in `_withdraw()` method. Let's say the withdrawal fee is 1%. So, when the last user withdraw their assets, the contract is left with 1% of stake. So, if the last users unstake 10000 **dStable** tokens, the contract will be left with 100 **dStable** tokens.

Now, if a new user will stake < 100 **dStable** tokens, it'll receive 0 shares. Because `previewDeposit()` will return 0 and `_deposit()` doesn't revert if shares is 0.

https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/main/contracts/vaults/dstake/DStakeToken.sol#L110-L131

**Attack Scenario**\
Users up to a certain amount will be receiving 0 shares but their **dstake** tokens will be taken.

**Recommendations**\
When shares is 0 method `_withdraw()` should revert.

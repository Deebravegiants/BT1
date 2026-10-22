# [M] withdrawalFeeBps_ should be multiplied by 100

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/76
Type: hats-finding

## Details
**Github username:** @aslanbekaibimov
  **Twitter username:** aslanbekaibimov
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/aslanbek)

  **Beneficiary:** 0x70E1f57646e1CA09D082A2027bFa965853f39ee0
  **Submission hash (on-chain):** 0x0432c44c79eb4c28796055a46e175df6442dbfc0a44c149ce25e5acb0abf4efb
  **Severity:** medium
  
  **Description:**
  **Description**\
In the contract SupportsWithdrawalFee, which is inherited by DStakeToken, withdrawalFeeBps_ is used with ONE_HUNDRED_PERCENT_BPS, which is equal to 1e6 (not 1e4 !). Therefore, this will lead to 100 times less fees being charged than intended.

```solidity
  function _calculateWithdrawalFee(
    uint256 assetAmount
  ) internal view returns (uint256) {
    return
      (assetAmount * withdrawalFeeBps_) /
      BasisPointConstants.ONE_HUNDRED_PERCENT_BPS;
  }
```

```solidity
  function _getGrossAmountRequiredForNet(
    uint256 netAmount
  ) internal view returns (uint256) {
    if (withdrawalFeeBps_ == 0) return netAmount;

    return
      (netAmount * BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
      (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS - withdrawalFeeBps_);
  }
```

**Attack Scenario**\
Not applicable. Whenever anyone redeems DStakeToken, the fee will always be 100 times smaller than intended.

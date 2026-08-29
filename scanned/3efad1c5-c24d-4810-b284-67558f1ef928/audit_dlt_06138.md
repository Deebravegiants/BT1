# [H] Loss of vault creator msg.value

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-24
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/83
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0x7ec93058030614963b3bf5a4f2e1b97c0d34cf5a43596b9367ae9b23e29c6bb5
**Severity:** high

**Description:**
**Description**\
As mentioned in docs:
- The security deposit of 1 gwei must be transferred with the call. This protects the vault stakers from the inflation attack described [here](https://github.com/OpenZeppelin/openzeppelin-contracts/issues/3706)

BUT it is not necessary for Stakewise vaults because vaults use the internal state for calculating shares not the balance of vaults:

_totalAssets is an internal state:
- Keeping track of the assets held by the vault internally removes the effect of direct transfers.
- Completely removes the inflation, removing all slippage
```
  function _convertToShares(
    uint256 assets,
    Math.Rounding rounding
  ) internal view returns (uint256 shares) {
    uint256 totalShares = _totalShares;
    // Will revert if assets > 0, totalShares > 0 and _totalAssets = 0.
    // That corresponds to a case where any asset would represent an infinite amount of shares.
    return
      (assets == 0 || totalShares == 0)
        ? assets
        : Math.mulDiv(assets, totalShares, _totalAssets, rounding);
  }
```
So it is a loss of funds for the vault creator.

**Impact**\

The Vault creator loses his msg.value for nothing

**Attachments**

**Revised Code File (Optional)**


_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/83_

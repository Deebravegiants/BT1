# [M] updateHighWaterMark can never be set to 0

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-21
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/45
Type: hats-finding

## Details
**Github username:** @@giorgiodalla
**Twitter username:** 0xAuditism
**Submission hash (on-chain):** 0x96e86d275474ea167cfa18efd11b6625924c5beb02fe3a357d85dd8df72dc369
**Severity:** medium

**Description:**
**Description**\
During the first deposit, the watermark is supposed to be set to 0, however the waterMark can never be set to 0 if it is >0 .
**Attack Scenario**\
There is no attack involved. It is just that it is clearly the protocol's intent to put it back to 0 for the first deposit, however this cannot be done

**Attachments**

1. **Proof of Concept (PoC) File**

```
    // If the total supply is zero, this is the first deposit, and tokens are minted based on the initial amount.
    if (_totalSupply == 0) {
      tokenAmount = assetManagementConfig().initialPortfolioAmount();
      // Reset the high watermark to zero if it's not the first deposit. //@note apparently this is just a mistake, this is supposed to happen.
  @>      feeModule().updateHighWaterMark(0);
    } else {
      // Calculate the amount of portfolio tokens to mint based on the deposit.
   tokenAmount = _getTokenAmountToMint(_depositRatio, _totalSupply);
    }
```
Here above we can clearly see that the intent is to set the waterMark to 0 when going through the first deposit.

```
  function _updateHighWaterMark(uint256 _currentPrice) internal {
    highWatermark = _currentPrice > highWatermark
      ? _currentPrice
      : highWatermark;
  }
```

Here above is the `_updateHighWaterMark` function that was called. However the `waterMark` is only set to the `_currentPrice` when it is bigger than the current highWatermark.
which means if `highWatermark` = 10, and  `_currentPrice` = 0, the highWatermark won't budge

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/45_

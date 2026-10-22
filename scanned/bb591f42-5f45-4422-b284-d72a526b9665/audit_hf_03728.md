# [M] Users that have to claim collateral more than once for a given time slot may get the wrong total amount

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 19857
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users that have to claim collateral more than once for a given time slot, may get the wrong total amount, because the amount claimed is incorrectly set. When letting a user claim his/her collateral, the code looks up the claimable amount, does an adjustment based on a factor, sends that amount to the user, then updates the remaining amount claimable. The code incorrectly sets the factor-adjusted total claimable amount as the amount claimed, rather than the claimable amount. Accounting of the claimed amount will be wrong, and the user will get less collateral back than they deserve, in some cases.

```solidity
// File: gmx-synthetics/contracts/market/MarketUtils.sol :
MarketUtils.claimCollateral()
#1
uint256 adjustedClaimableAmount =
Precision.applyFactor(claimableAmount, claimableFactor);

revert CollateralAlreadyClaimed(adjustedClaimableAmount,
claimedAmount);
}
uint256 remainingClaimableAmount = adjustedClaimableAmount -
claimedAmount;
dataStore.setUint(
Keys.claimedCollateralAmountKey(market, token, timeKey,
account),
adjustedClaimableAmount
);
MarketToken(payable(market)).transferOut(
token,
receiver,
remainingClaimableAmount
);
```
cts/market/MarketUtils.sol#L631-L647

• A user triggers claimable collateral for 1 Eth (claimableAmount = 1)
• A keeper sets claimableFactor to 1.0
• The user calls claim, and gets the full 1 Eth, and claimedAmount becomes 1 (adjustedClaimableAmount)
• A keeper sets claimableFactor to 0.5 for that time slot
• The user triggers more claimable collateral for 1 Eth (claimableAmount = 2) for the same time slot
• The user calls claim. adjustedClaimableAmount is 2 * 0.5 = 1, remainingClaimableAmount is 1 - 1 = 0, so the user can't claim anything. The user should have been able to claim a total of 1.5 Eth, but was only able to claim the original 1 Eth, and then nothing more.

## Recommendation
```diff
diff --git a/gmx-synthetics/contracts/market/MarketUtils.sol b/gmx-synthetics/contracts/market/MarketUtils.sol
index 7624b69..3346296 100644
--- a/gmx-synthetics/contracts/market/MarketUtils.sol
+++ b/gmx-synthetics/contracts/market/MarketUtils.sol
@@ -637,7 +637,7 @@ library MarketUtils {
dataStore.setUint(
Keys.claimedCollateralAmountKey(market, token, timeKey, account),
- adjustedClaimableAmount
+ claimableAmount
);
MarketToken(payable(market)).transferOut(
```

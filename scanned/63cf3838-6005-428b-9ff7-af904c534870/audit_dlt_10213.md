# [?] Add missing reentrancy protection in PendleYieldToken

## Summary
Severity: Unknown
Chain: Pendle
Component: pendle-finance/pendle-core-v2-public
Published: 2022-06-05
Source: https://github.com/pendle-finance/pendle-core-v2-public/commit/e9a726ea0276d5709fffd8d3b839781e9a50eba0
Type: security-commit

## Details
Add missing reentrancy protection in PendleYieldToken

## Patch
### contracts/core/PendleYieldToken.sol
```diff
@@ -133,14 +133,49 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
         emit RedeemReward(user, rewardsOut);
     }
 
-    function updateAndDistributeReward(address user) external {
+    function updateAndDistributeReward(address user) external nonReentrant {
         _updateAndDistributeRewards(user);
     }
 
     function updateAndDistributeInterest(address user) external nonReentrant {
         _updateAndDistributeInterest(user);
     }
 
+    /**
+     * @dev In case the pool is expired and there is left some SCY not yet redeemed from the contract, the rewards should
+     * be claimed before withdrawing to treasury.
+     *
+     * @dev And since the reward distribution (which based on users' dueInterest) stopped at the scyIndexBeforeExpiry, it is not
+     * necessary to updateAndDistributeRewandDistributeInterest along with reward here.
+     */
+    function withdrawFeeToTreasury() external nonReentrant {
+        address[] memory rewardTokens = _getRewardTokens();
+        if (isExpired()) {
+            _updateRewardIndex(); // as refered to the doc above
+        }
+
+        uint256 length = rewardTokens.length;
+        address treasury = IPYieldContractFactory(factory).treasury();
+        uint256[] memory amountRewardsOut = new uint256[](length);
+
+        for (uint256 i = 0; i < length; i++) {
+            address token = rewardTokens[i];
+            uint256 outAmount = totalRewardsPostExpiry[token];
+            if (outAmount > 0) IERC20(rewardTokens[i]).safeTransfer(treasury, outAmount);
+            totalRewardsPostExpiry[token] = 0;
+            amountRewardsOut[i] = outAmount;
+        }
+
+        uint256 totalScyFee = totalProtocolFee + totalInterestPostExpiry;
+        totalProtocolFee = totalInterestPostExpiry = 0;
+
+        if (totalScyFee > 0) {
+            IERC20(SCY).safeTransfer(treasury, totalScyFee);
+            _updateScyBalance();
+        }
+        emit WithdrawFeeToTreasury(amountRewardsOut, totalScyFee);
+    }
+
     function _redeemPY(address[] memory receivers, uint256[] memory amounts)
         internal
         returns (uint256 amountScyOut)
@@ -273,41 +308,6 @@ contract PendleYieldToken is PendleBaseToken, RewardManager, IPYieldToken, Reent
         }
     }
 
-    /**
-     * @dev In case the pool is expired and there is left some SCY not yet redeemed from the contract, the rewards should
-     * be claimed before withdrawing to treasury.
-     *
-     * @dev And since the reward distribution (which based on users' dueInterest) stopped at the scyIndexBeforeExpiry, it is not
-     * necessary to updateAndDistributeRewandDistributeInterest along with reward here.
-     */
-    function withdrawFeeToTreasury() public {
-        address[] memory rewardTokens = _getRewardTokens();
-        if (isExpired()) {
-            _updateRewardIndex(); // as refered to the doc above
-        }
-
-        uint256 length = rewardTokens.length;
-        address treasury = IPYieldContractFactory(factory).treasury();
-        uint256[] memory amountRewardsOut = new uint256[](length);
-
-        for (uint256 i = 0; i < length; i++) {
-            address token = rewardTokens[i];
-            uint256 outAmount = totalRewardsPostExpiry[token];
-            if (outAmount > 0) IERC20(rewardTokens[i]).safeTransfer(treasury, outAmount);
-            totalRewardsPostExpiry[token] = 0;
-            amountRewardsOut[i] = outAmount;
-        }
-
-        uint256 totalScyFee = totalProtocolFee + totalInterestPostExpiry;
-        totalProtocolFee = totalInterestPostExpiry = 0;
-
-        if (totalScyFee > 0) {
-            IERC20(SCY).safeTransfer(treasury, totalScyFee);
-            _updateScyBalance();
-        }
-        emit WithdrawFeeToTreasury(amountRewardsOut, totalScyFee);
-    }
-
     function _calcAmountToMint(uint256 amount) internal returns (uint256) {
         (, uint256 lastIndexBeforeExpiry) = getScyIndex();
         return SCYUtils.scyToAsset(lastIndexBeforeExpiry, amount);
```

# [M] Wrong calculation in for the first `updateState()` in `EthGenesisVault`

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-09-02
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/130
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0x9782007015bc3ccca358af8f32b53b83eecb6ccfdffaad9bfa733aca90ffc853
**Severity:** medium

**Description:**
**Description**\
In current implementation, for first `updatestate()` In `EthGenesisVault` is:
```solidity
// process total assets delta since last update
    int256 totalAssetsDelta = _harvestAssets(harvestParams);

    if (!isCollateralized) {
      // it's the first harvest, deduct rewards accumulated so far in legacy pool
      totalAssetsDelta -= SafeCast.toInt256(_rewardEthToken.totalRewards());
    }
    if (totalAssetsDelta != 0) { //Gas saving
    // fetch total assets controlled by legacy pool
    uint256 legacyPrincipal = _rewardEthToken.totalAssets() - _rewardEthToken.totalPenalty();

    // calculate total principal
    uint256 totalPrincipal = _totalAssets + legacyPrincipal;
    if (totalAssetsDelta < 0) {
      // calculate and update penalty for legacy pool
      int256 legacyPenalty = SafeCast.toInt256(
        Math.mulDiv(uint256(-totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(-legacyPenalty);
      // deduct penalty from total assets delta
      totalAssetsDelta += legacyPenalty;
    } else {
      // calculate and update reward for legacy pool
      int256 legacyReward = SafeCast.toInt256(
        Math.mulDiv(uint256(totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(legacyReward);
      // deduct reward from total assets delta
      totalAssetsDelta -= legacyReward;
    }
    }
    if (totalAssetsDelta != 0) {
      super._processTotalAssetsDelta(totalAssetsDelta);
    }
```
But there are some issues here, In the first `updatestate()`, first `updatestate()` is for setting `totalPenalty` in the `rewardETHToken` contract.

the first issue is that the calculation uses `_totalAssets` which is incorrect.
> `_totalAssets` is at least 1 `gwei` and it shouldn't used in the first calculation.

the second issue is that, at the end `_totalAssets` for v3 will be updated which is wrong and could create some issues. (Messing up the 1:1 share-to-asset ratio and making the vault vulnerable to share manipulation)

**Impact**\
 
 - wrong calculation for `totalPenalty`
 - Messing up the 1:1 share-to-asset ratio
 - Make the vault vulnerable to share manipulation

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
- For the first `updatestate()` don't use `_totalAsset`.
```diff
  function updateState(
    IKeeperRewards.HarvestParams calldata harvestParams
  ) public override(IVaultState, VaultState) {
    bool isCollateralized = IKeeperRewards(_keeper).isCollateralized(address(this));

    // process total assets delta since last update
    int256 totalAssetsDelta = _harvestAssets(harvestParams);

    if (!isCollateralized) {
      // it's the first harvest, deduct rewards accumulated so far in legacy pool
      totalAssetsDelta -= SafeCast.toInt256(_rewardEthToken.totalRewards());
+      if (totalAssetsDelta < 0) {
+	_rewardEthToken.updateTotalRewards(totalAssetsDelta);
+      } else { 
+        _rewardEthToken.updateTotalRewards(totalAssetsDelta);
+      }
+    } else {
+    // Vault isCollateralized 
    // fetch total assets controlled by legacy pool
    uint256 legacyPrincipal = _rewardEthToken.totalAssets() - _rewardEthToken.totalPenalty();

    // calculate total principal
    uint256 totalPrincipal = _totalAssets + legacyPrincipal;
    if (totalAssetsDelta < 0) {
      // calculate and update penalty for legacy pool
      int256 legacyPenalty = SafeCast.toInt256(
        Math.mulDiv(uint256(-totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(-legacyPenalty);
      // deduct penalty from total assets delta
      totalAssetsDelta += legacyPenalty;
    } else {
      // calculate and update reward for legacy pool
      int256 legacyReward = SafeCast.toInt256(
        Math.mulDiv(uint256(totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(legacyReward);
      // deduct reward from total assets delta
      totalAssetsDelta -= legacyReward;
    }

    if (totalAssetsDelta != 0) {
      super._processTotalAssetsDelta(totalAssetsDelta);
    }

    // update exit queue
    if (canUpdateExitQueue()) {
      _updateExitQueue();
    }
  }
  }
```

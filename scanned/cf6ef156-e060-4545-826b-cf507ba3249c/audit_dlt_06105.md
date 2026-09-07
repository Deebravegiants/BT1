# [M] Staking rewards cannot be updated due to incorrect usage of `SafeERC20.safeApprove`

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-22
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/42
Type: hats-finding

## Details
**Github username:** @aviggiano
**Submission hash (on-chain):** 0xc73327d922227ef04633cf85d0cc9855f74499615581a3b5bf6f4c8064544332
**Severity:** medium severity

**Description:**
# Staking rewards cannot be updated due to incorrect usage of `SafeERC20.safeApprove`

In [4bc89a3051dd4db80415933425b7d51e3d9a9240](https://github.com/VMEX-finance/vmex/commit/4bc89a3051dd4db80415933425b7d51e3d9a9240), a commit change introduced another issue on the `ExternalRewardDistributor.beginStakingReward` function. 

By using `IERC20(underlying).safeApprove(stakingContract, type(uint).max);`, the manager will not be able to update staking rewards, as `safeApprove` [reverts](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/fcf35e5722847f5eadaaee052968a8a54d03622a/contracts/token/ERC20/utils/SafeERC20.sol#L45-L58) when changing allowance from non-zero to non-zero.

# Severity

Medium. Manager cannot update staking rewards.

# Proof of Concept

Please review the following test

```
TS_NODE_TRANSPILE_ONLY=1 hardhat test ./test-suites/test-aave/__setup.spec.ts  ./test-suites/test-aave/incentives/external/configure.spec.ts
```

```diff
diff --git a/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol
index 8815218d..3f0164c7 100644
--- a/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol
+++ b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol
@@ -58,7 +58,8 @@ contract ExternalRewardDistributor is IExternalRewardsDistributor {
     require(!IAssetMappings(assetMappings).getAssetBorrowable(underlying), "Underlying cannot be borrowable for external rewards");
 
     stakingData[underlying][trancheId] = stakingContract;
-    IERC20(underlying).approve(stakingContract, type(uint).max);
+    // @audit-issue safeApprove reverts when changing allowance from non-zero to non-zero
+    IERC20(underlying).safeApprove(stakingContract, type(uint).max);
 
     //transfer all aToken's underlying to this contract and stake it
     uint256 amount = IERC20(aToken).totalSupply();
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/42_

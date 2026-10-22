# [M] `processYield

## Summary
Severity: Medium
Contest weight: 0.3466
Dataset id: 8313
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the yield‑distribution routine of the ConvexCurveLPVault contract, specifically in the `processYield()` function. This function iterates over the entire list of extra reward contracts returned by `extraRewardsLength()` and attempts to transfer each reward token to lenders. Because the iteration has no explicit bound or pagination, the gas consumption can grow linearly with the number of extra rewards and with the complexity of each token transfer. The root cause is the absence of an offset/length limitation that is employed elsewhere in the code base (e.g., `YieldManager.distributeYield()`). Consequently, if the Convex protocol or an attacker adds a large number of extra reward tokens, or if those tokens contain a small amount of dust that forces a transfer, the loop may exceed the block gas limit and cause the transaction to revert. When this revert happens, the entire yield‑distribution process aborts, leaving lenders without any of the expected yield payments. From the user’s perspective, balances that should show newly earned rewards remain unchanged or appear as zero, leading to confusion or panic as their expected refunds or interest never arrive. The issue manifests only when the extra‑reward array grows beyond a certain size or when malicious dust is introduced, making it a conditional denial‑of‑service (DoS) attack against the protocol’s accounting logic. It was uncovered during a manual audit review of the vault’s source code, where the unbounded loop was highlighted as a potential gas‑limit failure. Detecting the problem in production can be difficult because normal operation with a modest number of rewards proceeds without error, and the failure only appears under edge‑case conditions that may not be exercised in standard tests. To remediate the flaw, the contract should adopt a bounded iteration scheme similar to `YieldManager.distributeYield()`, adding offset and length parameters to limit each call’s workload, capping the number of extra rewards that can be processed in a single transaction, or otherwise enforcing a gas‑budget check. By doing so, the protocol can guarantee that yield distribution will complete reliably, preserving the expected financial outcomes for lenders and maintaining the integrity of the accounting model.

## Proof of Concept
The `processYield()` function loops over all of the extra rewards and transfers them

    File: smart-contracts/ConvexCurveLPVault.sol   #1

    105       uint256 extraRewardsLength = IConvexBaseRewardPool(baseRewardPool).extraRewardsLength();
    106       for (uint256 i = 0; i < extraRewardsLength; i++) {
    107         address _extraReward = IConvexBaseRewardPool(baseRewardPool).extraRewards(i);
    108         address _rewardToken = IRewards(_extraReward).rewardToken();
    109         _transferYield(_rewardToken);
    110       }

[ConvexCurveLPVault.sol#L105-L110](https://github.com/code-423n4/2022-05-sturdy/blob/78f51a7a74ebe8adfd055bdbaedfddc05632566f/smart-contracts/ConvexCurveLPVault.sol#L105-L110)  

There is no guarantee that the tokens involved will be efficient in their use of gas, and there are no upper bounds on the number of extra rewards:

        function extraRewardsLength() external view returns (uint256) {
            return extraRewards.length;
        }

        function addExtraReward(address _reward) external returns(bool){
            require(msg.sender == rewardManager, "!authorized");
            require(_reward != address(0),"!reward setting");

            extraRewards.push(_reward);
            return true;
        }

[BaseRewardPool.sol#L105-L115](https://github.com/convex-eth/platform/blob/main/contracts/contracts/BaseRewardPool.sol#L105-L115)  

Even if not every extra reward token has a balance, an attacker can sprinkle each one with dust, forcing a transfer by this function

`_getAssetYields()` has a similar issue:

    File: smart-contracts/YieldManager.sol   #X

    129       AssetYield[] memory assetYields = _getAssetYields(exchangedAmount);
    130       for (uint256 i = 0; i < assetYields.length; i++) {
    131         if (assetYields[i].amount > 0) {
    132           uint256 _amount = _convertToStableCoin(assetYields[i].asset, assetYields[i].amount);
    133           // 3. deposit Yield to pool for suppliers
    134           _depositYield(assetYields[i].asset, _amount);
    135         }
    136       }

[YieldManager.sol#L129-L136](https://github.com/code-423n4/2022-05-sturdy/blob/78f51a7a74ebe8adfd055bdbaedfddc05632566f/smart-contracts/YieldManager.sol#L129-L136)

## Recommendation
Include an offset and length as is done in `YieldManager.distributeYield()`.

Fix the issue of processYield()‘s run out of gas due to convex’s extra rewards sturdyfi/code4rena-may-2022#4](https://github.com/sturdyfi/code4rena-may-2022/pull/4)

I’ve considered this issue. The reason why I chose not to raise it up is because adding reward tokens is restricted on Convex’s side. Given the number of integrations they have, it’s unlikely that they will add too many tokens or gas-guzzling ones that will cause claims to run OOG.

Nevertheless, it is a possibility, albeit an unlikely one, so I’ll let the issue stand (also since the sponsor confirmed it).

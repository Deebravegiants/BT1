# [M] Adding a new tier will prevent rebasing

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-10
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/40
Type: hats-finding

## Details
**Github username:** @marjon-call
**Submission hash (on-chain):** 0x967dde36540009c9a5e595d49904de84f7a94848a5fe0aa0091676f814b99eef
**Severity:** medium

**Description:**
**Description**\
Adding a new tier causes an out of bounds revert whenever a rebase is called. 

**Issue Scenario**\
If `MembershipManager.addNewTier` is called `MembershipManager.rebase` can not be called due to an out-of-bounds in `GlobalIndexLibrary.calculateRewardsPerTierV0`:

```js
function calculateRewardsPerTierV0(address _membershipManager, address _liquidityPool, uint256 _ethRewardsAmountPerEEthShare) 
public view returns (uint256[] memory, uint24[] memory) {
    MembershipManager membershipManager = MembershipManager(payable(_membershipManager));
    LiquidityPool liquidityPool = LiquidityPool(payable(_liquidityPool));

    uint256 numberOfTiers = membershipManager.numberOfTiers();
    uint256[] memory tierRewards = new uint256[](numberOfTiers);
    uint24[] memory tierWeights = new uint24[](numberOfTiers);

    for (uint256 i = 0; i < numberOfTiers; i++) {
        (uint128 amounts, uint128 shares) = membershipManager.tierDeposits(i);
        (uint96 rewardsGlobalIndex, uint40 requiredTierPoints, uint24 weight,) = membershipManager.tierData(i);

        tierRewards[i] = _ethRewardsAmountPerEEthShare * shares / 1 ether;
        tierWeights[i] = weight;
    }

    return (tierRewards, tierWeights);
}
```

The cause is that number of tiers gets increased, while `membershipManager.tierDeposits` does not.

**Attachments**

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/libraries/GlobalIndexLibrary.sol#L61-L78

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/40_

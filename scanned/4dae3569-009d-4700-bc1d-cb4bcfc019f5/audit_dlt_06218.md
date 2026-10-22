# [M] The `MembershipManager.requestWithdrawAndBurn()` does not claim points and update the tier if needed

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-08
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/34
Type: hats-finding

## Details
**Github username:** @0xbepresent
**Submission hash (on-chain):** 0x569b2a28a220a96b99f2c67c1f04513abb2fe126978b9cb9906951a13d637174
**Severity:** medium

**Description:**
**Description**\

The user can use the [MembershipManager.requestWithdrawAndBurn()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L229C14-L229C36) or [MembershipManager.unwrapForEEthAndBurn()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L159C14-L159C34) functions in order to get the assets. The problem is that those functions don't call the [claim()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L247) function causing that the user can lose some rewards.

If an user has gained some points that allow him to claim a new tier, the user won't be changed to the new tier if he uses `requestWithdrawAndBurn()` or `unwrapForEEthAndBurn()` functions.

**Attack Scenario**\

Please consider the next scenario:

1. An user deposit to the MemebershipManager using the [wrapEth()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L145) function. At this point he is in `tier 0`.
2. Days go by and user get some points and he is able to claim to `tier 1` but he does not call the `claim()` function manually because he does not know he needs to do that in order to claim to the new tier.
3. User requests a withdraw calling the [MembershipManager.requestWithdrawAndBurn()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L229C14-L229C36) function. The function does not change the user to the new tier.
4. The withdraw proceeds but he will lost rewards accordly to the `tier 1` because `requestWithdrawAndBurn()` does not claim the user points and change the tier.

**Attachments**

1. **Proof of Concept (PoC) File**

I created the next test where Alice is able to claim `the tier 1` because Alice has staking for 28 days but at the end she only calls `requestWithdrawAndBurn()` thinking that the function will change the tier to the tier 1. At the end she get the rewards from the `tier 0` which is wrong because she must have rewards from the `tier 1`.

```solidity
    function test_pointsAreNotClaimedOnRequestWithdrawAndBurn() public {
        vm.deal(alice, 1 ether);
        vm.startPrank(alice);
        //
        // Alice mints an NFT with 2 points by wrapping 2 ETH and starts earning points
        uint256 aliceToken = membershipManagerV1Instance.wrapEth{value: 1 ether}(1 ether, 0);
        assertEq(alice.balance, 0 ether);
        assertEq(address(liquidityPoolInstance).balance, 1 ether);
        assertEq(eETHInstance.balanceOf(alice), 0 ether);
        assertEq(membershipNftInstance.valueOf(aliceToken), 1 ether);
        //
        // Alice's NFT's points start from 0 and the claimableTier is 0
        assertEq(membershipNftInstance.loyaltyPointsOf(aliceToken), 0);
        assertEq(membershipNftInstance.tierPointsOf(aliceToken), 0);
        assertEq(membershipNftInstance.claimableTier(aliceToken), 0);
        //
        // Alice's NFT's points grow and claimableTier is 0
        skip(1 days);
        assertEq(membershipNftInstance.loyaltyPointsOf(aliceToken), kwei);
        assertEq(membershipNftInstance.tierPointsOf(aliceToken), 24);
        assertEq(membershipNftInstance.claimableTier(aliceToken), 0);
        //
        // The claimableTier now is 1
        skip(27 days);
        uint40 currentTierPointsOf = membershipNftInstance.tierPointsOf(aliceToken);
        uint40 currentLoyaltyPointsOf = membershipNftInstance.loyaltyPointsOf(aliceToken);
        assertEq(currentLoyaltyPointsOf, 28 * kwei);
        assertEq(currentTierPointsOf, 24 * 28);
        assertEq(membershipNftInstance.claimableTier(aliceToken), 1);
        vm.stopPrank();
        //
        // Bob in
        vm.deal(bob, 2 ether);
        vm.startPrank(bob);
        uint256 bobToken = membershipManagerV1Instance.wrapEth{value: 2 ether}(2 ether, 0);
        vm.stopPrank();
        //
        // Alice has 1 ether, bob has 2 ether
        assertEq(membershipNftInstance.valueOf(aliceToken), 1 ether);
        assertEq(membershipNftInstance.valueOf(bobToken), 2 ether);
        assertEq(address(liquidityPoolInstance).balance, 3 ether);
        //
        // More Staking rewards 1 ETH into LP
        vm.startPrank(address(etherFiAdminInstance));
        membershipManagerV1Instance.rebase(1 ether);
        vm.stopPrank();
        //
        // Alice can claim to the tier 1 with the weight 2 but she calls
        // requestWithdrawAndBurn lossing the rewards for tier 1
        assertEq(membershipNftInstance.claimableTier(aliceToken), 1);
        // Bob belongs to the tier 0 with the weight 1
        uint256 aliceWeightedRewardsUsingTier0 = 1 * 1 ether * 1 / uint256(3);
        uint256 bobWeightedRewards = 1 * 1 ether * 2 / uint256(3);
        uint256 sumWeightedRewards = aliceWeightedRewardsUsingTier0 + bobWeightedRewards;
        uint256 sumRewards = 1 ether;
        uint256 aliceRescaledRewards = aliceWeightedRewardsUsingTier0 * sumRewards / sumWeightedRewards;
        uint256 bobRescaledRewards = bobWeightedRewards * sumRewards / sumWeightedRewards;
        assertEq(membershipNftInstance.valueOf(aliceToken), 1 ether + aliceRescaledRewards - 1); // some rounding errors
        assertEq(membershipNftInstance.valueOf(bobToken), 2 ether + bobRescaledRewards - 1); // some rounding errors
        //
        // Alice's NFT unwraps all her remaining membership points, burning the NFT
        // she lost the rewards for tier 1 because the requestWithdrawAndBurn never calls claim() function
        vm.startPrank(alice);
        uint256 aliceRequestId2 = membershipManagerV1Instance.requestWithdrawAndBurn(aliceToken);
        vm.stopPrank();
        // get the assets
        _finalizeWithdrawalRequest(aliceRequestId2);
        vm.startPrank(alice);
        withdrawRequestNFTInstance.claimWithdraw(aliceRequestId2);
        assertEq(membershipNftInstance.balanceOf(alice, aliceToken), 0); 
        //
        // Alice gets rewards from the tier 0 using the weight 1 instead of tier 1 with weight 2
        assertEq(alice.balance, 1 ether + aliceWeightedRewardsUsingTier0 - 1);
        vm.stopPrank();
    }
```


2. **Revised Code File (Optional)**

The [MembershipManager.requestWithdrawAndBurn()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L229C14-L229C36) and [MembershipManager.unwrapForEEthAndBurn()](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/MembershipManager.sol#L159C14-L159C34) should claim the points and update the tier if needed before the user exits his position:

```diff
    function requestWithdrawAndBurn(uint256 _tokenId) external whenNotPaused returns (uint256) {
        _requireTokenOwner(_tokenId);

        // Claim all staking rewards before burn
--      _claimStakingRewards(_tokenId);
--      _migrateFromV0ToV1(_tokenId);
++      claim(_tokenId);

        (uint256 totalBalance, uint256 feeAmount) = _withdrawAndBurn(_tokenId);

        eETH.approve(address(liquidityPool), totalBalance);
        uint256 withdrawTokenId = liquidityPool.requestMembershipNFTWithdraw(msg.sender, totalBalance, feeAmount);
        
        return withdrawTokenId;
    }
```

```diff
    function unwrapForEEthAndBurn(uint256 _tokenId) external whenNotPaused {
        _requireTokenOwner(_tokenId);

        // Claim all staking rewards before burn
--      _claimStakingRewards(_tokenId);
--      _migrateFromV0ToV1(_tokenId);
++      claim(_tokenId);

        uint40 loyaltyPoints = membershipNFT.loyaltyPointsOf(_tokenId);
        (uint256 totalBalance, uint256 feeAmount) = _withdrawAndBurn(_tokenId);

        // transfer 'eEthShares' of eETH to the owner
        eETH.transfer(msg.sender, totalBalance - feeAmount);

        if (feeAmount > 0) {
            liquidityPool.withdraw(address(this), feeAmount);
        }

        emit NftUnwrappedForEEth(msg.sender, _tokenId, totalBalance - feeAmount, loyaltyPoints, feeAmount);
    }
```

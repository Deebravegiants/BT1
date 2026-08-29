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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/34_

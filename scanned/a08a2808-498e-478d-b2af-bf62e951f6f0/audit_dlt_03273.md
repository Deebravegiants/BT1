# [M] Potential Loss of Rewards During Token Transfers in StaticATokenLM.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-01
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/4
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L367-L386


# Vulnerability details

## Impact
This issue could lead to a permanent loss of rewards for the transferer of the token. During the token transfer process, the `_beforeTokenTransfer` function updates rewards for both the sender and the receiver. However, due to the specific call order and the behavior of the `_updateUser` function and the `_getPendingRewards` function, some rewards may not be accurately accounted for.

The crux of the problem lies in the fact that the `_getPendingRewards` function, when called with the `fresh` parameter set to `false`, may not account for all the latest rewards from the `INCENTIVES_CONTROLLER`. As a result, the `_updateUserSnapshotRewardsPerToken` function, which relies on the output of the `_getPendingRewards` function, could end up missing out on some rewards. This could be detrimental to the token sender, especially the `Backing Manager` whenever `RToken` is redeemed. Apparently, most users having wrapped their `AToken`, would automatically use it to issue `RToken` as part of the basket range of backing collaterals and be minimally impacted. But it would have the Reserve  Protocol collectively affected depending on the frequency and volume of RToken redemption and the time elapsed since `_updateRewards()` or `_collectAndUpdateRewards()` was last called. The same impact shall also apply when making token transfers to successful auction bidders. 

## Proof of Concept
As denoted in the function NatSpec below, function `_beforeTokenTransfer` updates rewards for senders and receivers in a [`transfer`](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/vendor/ERC20.sol#L223-L250).

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L367-L386

```solidity
   /**
     * @notice Updates rewards for senders and receiver in a transfer (not updating rewards for address(0))
     * @param from The address of the sender of tokens
     * @param to The address of the receiver of tokens
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256
    ) internal override {
        if (address(INCENTIVES_CONTROLLER) == address(0)) {
            return;
        }
        if (from != address(0)) {
            _updateUser(from);
        }
        if (to != address(0)) {
            _updateUser(to);
        }
    }
```
When function `_updateUser` is respectively invoked, `_getPendingRewards(user, balance, false)` is called. 

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L543-L550

```solidity
    /**
     * @notice Adding the pending rewards to the unclaimed for specific user and updating user index
     * @param user The address of the user to update
     */
    function _updateUser(address user) internal {
        uint256 balance = balanceOf(user);
        if (balance > 0) {
            uint256 pending = _getPendingRewards(user, balance, false);
            _unclaimedRewards[user] = _unclaimedRewards[user].add(pending);
        }
        _updateUserSnapshotRewardsPerToken(user);
    }
```

However, because the third parameter has been entered `false`, the third if block of function `_getPendingRewards` is skipped.

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L552-L591

```solidity
    /**
     * @notice Compute the pending in RAY (rounded down). Pending is the amount to add (not yet unclaimed) rewards in RAY (rounded down).
     * @param user The user to compute for
     * @param balance The balance of the user
     * @param fresh Flag to account for rewards not claimed by contract yet
     * @return The amound of pending rewards in RAY
     */
    function _getPendingRewards(
        address user,
        uint256 balance,
        bool fresh
    ) internal view returns (uint256) {
        if (address(INCENTIVES_CONTROLLER) == address(0)) {
            return 0;
        }

        if (balance == 0) {
            return 0;
        }

        uint256 rayBalance = balance.wadToRay();

        uint256 supply = totalSupply();
        uint256 accRewardsPerToken = _accRewardsPerToken;

        if (supply != 0 && fresh) {
            address[] memory assets = new address[](1);
            assets[0] = address(ATOKEN);

            uint256 freshReward = INCENTIVES_CONTROLLER.getRewardsBalance(assets, address(this));
            uint256 lifetimeRewards = _lifetimeRewardsClaimed.add(freshReward);
            uint256 rewardsAccrued = lifetimeRewards.sub(_lifetimeRewards).wadToRay();
            accRewardsPerToken = accRewardsPerToken.add(
                (rewardsAccrued).rayDivNoRounding(supply.wadToRay())
            );
        }

        return
            rayBalance.rayMulNoRounding(accRewardsPerToken.sub(_userSnapshotRewardsPerToken[user]));
    }
```

Hence, `accRewardsPerToken` may not be updated with the latest rewards from `INCENTIVES_CONTROLLER`. Consequently, `_updateUserSnapshotRewardsPerToken(user)` will miss out on claiming some rewards and is a loss to the StaticAtoken transferrer.

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L531-L537

```solidity
    /**
     * @notice Update the rewardDebt for a user with balance as his balance
     * @param user The user to update
     */
    function _updateUserSnapshotRewardsPerToken(address user) internal {
        _userSnapshotRewardsPerToken[user] = _accRewardsPerToken;
    }
```
Ironically, this works out as a zero-sum game where the loss of the transferrer is a gain to the transferee. But most assuredly, the Backing Manager is going to end up incurring more losses than gains in this regard.  

## Tools Used
Manual

## Recommended Mitigation Steps
Consider introducing an additional call to update the state of rewards before any token transfer occurs. Specifically, within the `_beforeTokenTransfer` function, invoking [`_updateRewards`](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L388-L415) like it has been implemented in [`StaticATokenLM._deposit`](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L309) and [`StaticATokenLM._withdraw`](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L336) before updating the user balances would have the issues resolved.

This method would not force an immediate claim of rewards, but rather ensure the internal accounting of rewards is up-to-date before the transfer. By doing so, the state of rewards for each user would be accurate and ensure no loss or premature gain of rewards during token transfers.








## Assessed type

Token-Transfer

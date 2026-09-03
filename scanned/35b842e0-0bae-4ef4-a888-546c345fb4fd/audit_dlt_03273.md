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

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/4_

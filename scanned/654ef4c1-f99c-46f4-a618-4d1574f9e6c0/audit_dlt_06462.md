# [M] Fee-on-Transfer Tokens in `createCampaigns` Function cause revert in  `_processRewardClaim`.

## Summary
Severity: Medium
Chain: Smart contract
Component: Metrom
Published: 2024-05-20
Source: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/1
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xd972c2f66bb2ea8981fdfbe887602d67b1b14a0e0f5c7d7aa917c3298cb29bb1
**Severity:** medium

**Description:**
**Description**
As mentioend by sponsers any ERC 20 is allowed, there are several ERC20 tokens that take a small fee on transfers/transferFroms (known as "[fee-on-transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer)" tokens). For these tokens, it should not be assumed that if you transfer x tokens to an address, the address actually receives x tokens. In the `createCampaigns` function, the amount used for calculations is assumed to be the amount transferred. However, the contract will have `amount - fee` in its balance, causing the `_processRewardClaim` function to revert and resulting in funds being stuck in the contract.

```solidity
                uint256 _feeAmount = _amount * _fee / UNIT;
                uint256 _rewardAmountMinusFees = _amount - _feeAmount;
                claimableFees[_token] += _feeAmount;

                _feeAmounts[_j] = _feeAmount;
                _rewardAmountsMinusFees[_j] = _rewardAmountMinusFees;

                Reward storage reward = campaign.reward[_token];
                reward.amount = _rewardAmountMinusFees;
                reward.unclaimed = _rewardAmountMinusFees;

                IERC20(_token).safeTransferFrom(msg.sender, address(this), _amount);
```

**Attack Scenario**
A user wants to create a campaign and uses [fee-on-transfer](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#fee-on-transfer) tokens, setting the amount as 1000. The contract assumes 1000 tokens are transferred, but only `1000 - fee` tokens are actually transferred to the contract, leading to potential reverts when `_processRewardClaim` is called.

**Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Calculate the balance before and after the transfer and use the difference for the amount variable.

```diff
+                uint256 balanceBefore = IERC20(_token).balanceOf(address(this));
+                IERC20(_token).safeTransferFrom(msg.sender, address(this), _amount);
+                uint256 balanceAfter = IERC20(_token).balanceOf(address(this));
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/1_

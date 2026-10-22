# [M] Use A's staked token balance can be used to

## Summary
Severity: Medium
Contest weight: 0.5938
Dataset id: 20187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
User's staked token balance can be used to mint option token as reward if the payout token equals to the stake token, can cause user to loss fund. In OTLM, user can stake stakeToken in exchange for the option token minted from the payment token. When staking, we transfer the stakedToken in the OTLM token.
```solidity
// Increase the user's stake balance and the total balance
stakeBalance[msg.sender] = userBalance + amount_;
totalBalance += amount_;
// Transfer the staked tokens from the user to this contract
stakedToken.safeTransferFrom(msg.sender, address(this), amount_);
```
Before the stake or unstake or when we are calling claimReward, we are calling _claimRewards -> _claimEpochRewards -> we use payout token to mint and create option token as reward.
```solidity
payoutToken.approve(address(optionTeller), rewards);
optionTeller.create(optionToken, rewards);
// Transfer rewards to sender
ERC20(address(optionToken)).safeTransfer(msg.sender, rewards);
```
The problem is, if the stake token and the payout token are the same token, the protocol does not distinguish the balance of the stake token and the balance of payout token. Suppose both stake token and payout token are USDC. Suppose user A stake 100 USDC. Suppose user B stake 100 USDC. Time passed, user B accrue 10 token unit reward. Now user B can claimRewards, the protocol use 10 USDC to mint option token for B. The OTLM has 190 USDC. If user A and user B both call emergencyUnstakeAll, whoever calls this function later will suffer a revert and he is not able to even give up the reward and claim their staked balance back. Because a part of the his staked token balance is treated as the payout token to mint option token reward for other user. If there are insufficient payout token in the OTLM, the expected behavior is that the transaction revert when claim the reward and when the code use payout token to mint option token. And in the worst case, user can call emergencyUnstakeAll to get their original staked balance back and give up their reward. However, if the staked token is the same as the payout token, a part of the user staked token can be mistakenly and constantly minted as option token reward for his own or for other user and eventually when user call emergencyUnstakeAll, there will be insufficient token balance and transaction revert. So user will not able to get their staked token back.

## Recommendation
Separate the accounting of the staked user and the payout token or check that staked token is not payout token when creating the OTLM.sol.

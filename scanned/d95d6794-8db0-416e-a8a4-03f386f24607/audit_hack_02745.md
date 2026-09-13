# [M] Claimed reward is not sent to liquidity mining immediately

## Summary
Severity: Medium
Reporter: minhquanym
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L102-L103
Type: audit-issue

## Details
# Claimed reward is not sent to liquidity mining immediately

## Vulnerability Detail
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L102-L103

In `TrueFiStrategy._deposit()` function, it called `stake()` on TrueMultiFarm. And in TrueMultiFarm, when calling `stake()`, it also claims reward for sender
```solidity
function stake(IERC20 token, uint256 amount) external override hasShares(token) update(token) {
    if (stakerRewards[token].claimableReward[msg.sender] > 0) {
        _claim(token);
    }
    stakes[token].staked[msg.sender] = stakes[token].staked[msg.sender].add(amount);
    stakes[token].totalStaked = stakes[token].totalStaked.add(amount);

    token.safeTransferFrom(msg.sender, address(this), amount);
    emit Stake(token, msg.sender, amount);
}
```

These reward token is not sent to `LIQUIDITY_MINING_RECEIVER` immediately but instead stay in TrueFiStrategy. It can make liquidity mining distribute reward with lower rate than expected.

## Impact
Claimed reward is not sent to liquidity mining immediately can make liquidity mining rate lower than expected.

## Proof of Concept
Calling `stake()` in TrueMultiFarm will also call `_claim()` if it's possible.
```solidity
function stake(IERC20 token, uint256 amount) external override hasShares(token) update(token) {
    if (stakerRewards[token].claimableReward[msg.sender] > 0) {
        _claim(token);
    }
    stakes[token].staked[msg.sender] = stakes[token].staked[msg.sender].add(amount);
    stakes[token].totalStaked = stakes[token].totalStaked.add(amount);

    token.safeTransferFrom(msg.sender, address(this), amount);
    emit Stake(token, msg.sender, amount);
}
```

And `_claim()` will send reward to sender. [Line 226](https://etherscan.io/address/0x4af280d9e794b5ea6bee039a6f48a6eafd865341#code#F10#L226)
```solidity
function _claim(IERC20 token) internal {
    uint256 rewardToClaim = stakerRewards[token].claimableReward[msg.sender];

    stakerRewards[token].totalClaimedRewards = stakerRewards[token].totalClaimedRewards.add(rewardToClaim);
    farmRewards.totalClaimedRewards = farmRewards.totalClaimedRewards.add(rewardToClaim);

    stakerRewards[token].claimableReward[msg.sender] = 0;
    farmRewards.claimableReward[address(token)] = farmRewards.claimableReward[address(token)].sub(rewardToClaim);

    rewardToken.safeTransfer(msg.sender, rewardToClaim);
    emit Claim(token, msg.sender, rewardToClaim);
}
```

## Tool used

Manual Review

## Recommendation

Consider send claimed reward immediately after calling `stake()`

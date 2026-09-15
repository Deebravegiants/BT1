# [H] Locked reward because `TrueMultiFarm.claim()` will return stkTRU instead of TRU token

## Summary
Severity: High
Reporter: minhquanym
Source: https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueMultiFarm.sol#L232-L245
Type: audit-issue

## Details
# Locked reward because `TrueMultiFarm.claim()` will return stkTRU instead of TRU token 

## Vulnerability Detail

In `TrueFiStategy.claimReward()`, it handles TRU claiming and sending to LIQUIDITY_MINING. But if TrueMultiFarm returns different token than TRU, it cannot be handled and will be locked.

In the link provided `TrueFiStrategy`, calling `TrueMultiFarm.claim()` will return stkTRU instead of TRU token.
https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueMultiFarm.sol#L232-L245

```solidity=232
function _claim(IERC20 token) internal {
    uint256 rewardToClaim = stakerRewards[token].claimableReward[msg.sender];

    stakerRewards[token].totalClaimedRewards = stakerRewards[token].totalClaimedRewards.add(rewardToClaim);
    farmRewards.totalClaimedRewards = farmRewards.totalClaimedRewards.add(rewardToClaim);

    stakerRewards[token].claimableReward[msg.sender] = 0;
    farmRewards.claimableReward[address(token)] = farmRewards.claimableReward[address(token)].sub(rewardToClaim);

    tru.safeApprove(address(stkTru), rewardToClaim);
    stkTru.stake(rewardToClaim);
    stkTru.safeTransfer(msg.sender, stkTru.balanceOf(address(this)));
    emit Claim(token, msg.sender, rewardToClaim);
}
```

Currently, mainnet version of TrueMultiFarm still return `TRU` as TrueFiStrategy expected. But since it implemented proxy, TrueFi can upgrade it anytime and when they do so, TrueFiStrategy will not be able to use stkTRU returned from TrueMultiFarm, resulted in these tokens locked in contract.

## Impact

Locked reward from TrueMultiFarm

## Proof of Concept

Reward token is hardcoded in TrueFiStrategy
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L65-L66

And in `claimReward()` it only handles sending `rewardToken` to liquidity mining
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L196-L200

## Tool used

Manual Review

## Recommendation

Since TrueMultiFarm implemented proxy, they can change implementation in anyway they want. So I think we have to monitor their action, withdraw funds when they announce to upgrade contract.

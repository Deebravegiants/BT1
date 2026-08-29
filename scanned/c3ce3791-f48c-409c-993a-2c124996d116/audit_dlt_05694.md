# [M] malicious user can front run any call to the sw...

## Summary
Severity: Medium
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30613%20-%20%5BSC%20-%20Medium%5D%20malicious%20user%20can%20front%20run%20any%20call%20to%20the%20sw....md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/Bribe.sol

## Description

## Brief/Intro

the function `voter.sol#swapReward` is meant to be used to update the reward token from old one to new one, this function is only callable by the admin and it make calls to the `Bribe.sol#swapOutRewardToken` which it updates the `isReward` from false to true for the newToken, and it set the old token index to the newToken address, however an attacker can front run the owner and cause Griefing plus preventing from setting the correct index to the newToken address, this issue can make loss to the owner by front run his/her TX and cause loss of gas + making the rewards length longer each time the attacker front run the owner call and preventing setting the correct index to the new token that the owner decide to set.

## Vulnerability Details

to call the swapReward function the owner first need to call the whitelist function to add the new token to whitelist, if not then the call to the swapReward is impossible because of the checks for the whitelist token the function `swapReward` make call to the swapOutRewardToken with the below inputs:

```solidity
 function swapReward(address gaugeAddress, uint256 tokenIndex, address oldToken, address newToken) external {
        require(msg.sender == admin, "only admin can swap reward tokens");
        IBribe(bribes[gaugeAddress]).swapOutRewardToken(tokenIndex, oldToken, newToken);
    }
```

as it shown the tokenIndex is set to update the token index when call made to the `swapOutRewardToken`:

```solidity
 function swapOutRewardToken(uint256 oldTokenIndex, address oldToken, address newToken) external {
        require(msg.sender == voter, "Only voter can execute");
        require(IVoter(voter).isWhitelisted(newToken), "New token must be whitelisted");
        require(rewards[oldTokenIndex] == oldToken, "Old token mismatch");

        // Check that the newToken does not already exist in the rewards array
        for (uint256 i = 0; i < rewards.length; i++) {
            require(rewards[i] != newToken, "New token already exists");
        }

        isReward[oldToken] = false;
        isReward[newToken] = true;

        // Since we've now ensured the new token doesn't exist, we can safely update
        rewards[oldTokenIndex] = newToken; // set the old index to the new token
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30613%20-%20%5BSC%20-%20Medium%5D%20malicious%20user%20can%20front%20run%20any%20call%20to%20the%20sw....md_

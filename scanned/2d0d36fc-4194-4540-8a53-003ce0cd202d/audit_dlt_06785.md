# [H] `BathBuddy` rewards DoS

## Summary
Severity: High
Chain: Smart contract
Component: 2023-04-rubicon
Published: 2023-04-13
Source: https://github.com/code-423n4/2023-04-rubicon-findings/issues/854
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-04-rubicon/blob/511636d889742296a54392875a35e4c0c4727bb7/contracts/periphery/BathBuddy.sol#L121-L135
https://github.com/code-423n4/2023-04-rubicon/blob/511636d889742296a54392875a35e4c0c4727bb7/contracts/periphery/BathBuddy.sol#L139-L155


# Vulnerability details

## Impact

As described in the docs, Rubicon protocol allows users to act as as liquidity providers (LPs), by providing funds and receiving `bathToken` in return, which can be used to obtain rewards through `BathBuddy` contract.  But `BathBuddy` internal logic allows any user to DoS reward distribution to smalls LPs by constantly calling `getReward` at small intervals. This is specially effective against small LPs. This finding should be classified as having medium severity, even though no funds are at risk,  the attacker can affect the protocol's functionality for an indefinite period of time.

## Proof of Concept

`BathBuddy`'s user rewards are calculated as shown below.

```solidity
function earned(
        address account,
        address token
    ) public view override returns (uint256) {
        require(friendshipStarted, "I have not started a bathToken friendship");

        return
            IERC20(myBathTokenBuddy) // Care with this?
                .balanceOf(account)
                .mul(
                    rewardPerToken(token).sub(
                        userRewardsPerTokenPaid[token][account]
                    )
                )
                .div(1e18)
                .add(tokenRewards[token][account]);
    }
```

Where `rewardPerToken`  values are updated by calling the `rewardPerToken` function.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-04-rubicon-findings/issues/854_

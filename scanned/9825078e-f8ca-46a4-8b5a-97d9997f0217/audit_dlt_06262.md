# [H] `_updateAccount` does not update the user's lastMaxLockDuration, which allows him to infinitely increase his portalEnergy to any value

## Summary
Severity: High
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-15
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/5
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xb90c2d6a41f412144029306aee959c6ad37728fcebd09c1f9f814c67bb7a8912
**Severity:** high

**Description:**
**Description**\
PortalEnergy has value as it can be sold for Possum(PSM) tokens via `sellPortalEnergy`.
One way a user's PortalEnergy gets updated is in the [`_updateAccount`](https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L225) function.
A user's portalEnergy gets incremented by portalEnergyEarned+portalEnergyIncrease:

```solidity
function _updateAccount(){
    ...
    accounts[_user].portalEnergy +=
        portalEnergyEarned +
        portalEnergyIncrease;
    ...
}
```

This issue describes how a user can infinitely increase his portalEnergy through the `portalEnergyIncreased` variable by updating the global maxLockDuration, then unstaking 0 amount of tokens multiple times in a loop.

This is possible because portalEnergyIncreased gets increased whenever there is a positive change between maxLockDuration and the user's lastMaxLockDuration, but after each update, the user's lastMaxLockDuration does not get updated.

```solidity
function _updateAccount(){
    ...
    uint256 portalEnergyIncrease = (accounts[_user].stakedBalance *
        (maxLockDuration - accounts[_user].lastMaxLockDuration) +
        (_amount * maxLockDuration)) / SECONDS_PER_YEAR;
    ...
}
```

This is of high severity because a user can increase his portal energy(which is an asset) to any value and contract can be drained of all Possum(PSM) tokens

**Attack Scenario**\

- Let's say a minute has passed since creation, user calls updateMaxLockDuration, which sets maxLockDuration to 7200
- User stake 100 principalToken
  - maxStakeDebt gets updated to 100\*7200/31536000
  - user lastMaxLockDuration=7200
  - user portalEnergy=7200
- User waits for a minute and calls updateMaxLockDuration, so maxLockDuration gets updated to 14400
- As many times as possible, e.g. within a loop of another contract, user does the following:
  - User unstakes 0 principalToken, which will \_updateAccount
    - portalEnergyEarned gets increased(but this is not our focus)
    - portalEnergyIncrease gets increased by:
      - (100*(14400-7200)+(0*14400))/31536000=
  - Repeat
  - This means that user's portalEnergy gets increased as well because portalEnergy=portalEnergyEarned+portalEnergyIncrease
- Since User has been able to increase his portalEnergy to any value, he can `sellPortalEnergy` for almost all PSM available in contract, and then unstake.


**Attachments**

1. **Proof of Concept (PoC) File**
See steps in attack scenario

2. **Revised Code File (Optional)**

The root cause of this issue is that user's lastMaxLockDuration gets set only once, which is during his first `stake` call, and does not get set whenever `_updateAccount` gets called.

Consider updating user's lastMaxLockDuration to the current maxLockDuration within the `_updateAccount` function.

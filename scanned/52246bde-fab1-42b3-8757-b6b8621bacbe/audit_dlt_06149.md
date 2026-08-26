# [M] Users can front-run the owner and update the rewards if the rewardsMinOracles hasn't been set yet

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-21
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/13
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0xe054cacf7e617c9ace765a94f966fbd8be85d0a8e2eab72b908cf4ff90deb9b2
**Severity:** medium

**Description:**
**Description**\

In KeeperRewards.sol, there is a function updateRewards() that calls internal _verifySignatures and provide rewardsMinOracles as the parameter. However, if it's not set yet, the rewards can be updated without any oracle signatures. 

**Attack Scenario**\

1. User provides params inside of updateRewards() function and front-runs setRewardsMinOracles() (maybe the owner wasn't able to call it right away due to high network congestion or high gas costs and the delay also has passed so the user can update the rewards basically without any oracle signatures because they will be set to 0.

2. The check inside of _verifySignatures() is bypassed:

https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperOracles.sol#L86-88 as requiredSignatures == 0

3. _verifySignature is internal view function that doesn't return anything (bool, for example), so after the call the state is updated as _verifySignature() is not reverted.

**Attachments**

1. **Proof of Concept (PoC) File**
Provided above.

2. **Revised Code File (Optional)**
https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperOracles.sol#L78-112
https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L93-106
https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L218-233


Mitigation: rewardsMinOracles should be set in the constructor right away and then use setRewardsMinOracles function as the ability to update the value.

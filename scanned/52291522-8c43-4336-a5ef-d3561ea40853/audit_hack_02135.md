# [M] Rewards can be migrated to an arbitrary address at anytime by owner

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2021-07-wildcredit/blob/82c48d73fd27a9d4d5d4a395b3affcef4ef6c5c8/contracts/RewardDistribution.sol#L180-L183
Type: audit-issue

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The migrateRewards() function which is onlyOwner takes recipient and amount parameters, which effectively allows owner to migrate the contract’s entire rewardToken balance at any time to that address. 

While the stated purpose is that this “Allows to migrate rewards to a new staking contract”, it is risky because it may give a perception of owner centralization to the protocol users/community. This could also be dangerous if triggered accidentally especially by an EOA owner address or maliciously via compromised keys.

## Proof of Concept

https://github.com/code-423n4/2021-07-wildcredit/blob/82c48d73fd27a9d4d5d4a395b3affcef4ef6c5c8/contracts/RewardDistribution.sol#L180-L183

See similar concern on migrate() functionality in ShibaSwap recently:
Yearn dev
https://twitter.com/bantg/status/1412370758987354116
https://twitter.com/bantg/status/1412388385663164425
Others
https://twitter.com/valentinmihov/status/1412352490918625280
https://twitter.com/shegenerates/status/1412642215537545218


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Evaluate the need for this function and avoid/mitigate risk appropriately.

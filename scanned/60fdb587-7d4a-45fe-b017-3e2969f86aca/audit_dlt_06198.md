# [M] The initial allocation of the staking rewards for a B-NFT holder and a T-NFT holder would be wrong

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-16
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/55
Type: hats-finding

## Details
**Github username:** @0xmuxyz
**Twitter username:** --
**Submission hash (on-chain):** 0x7ce33002f70a6cf188d4bbe2cebb8fe25a2d023b1af93a87ad0db0946f339555
**Severity:** medium

**Description:**
## Description
Within the EtherFiNodesManager contract, the `stakingRewardsSplit` would be defined to store the data for the staking rewards allocation like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L48
```solidity
    //Holds the data for the revenue splits depending on where the funds are received from
    RewardsSplit public stakingRewardsSplit;
```

When a partial withdrawal to skim the staking rewards, the allocation of the staking rewards would be calculated based on the `stakingRewardsSplit` via the EtherFiNodesManager#`getRewardsPayouts()` like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L606

Within the EtherFiNodesManager#`initialize()`, an initial allocation of the staking rewards would be set to the `stakingRewardsSplit` like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L120-L125
```solidity
    function initialize(
        address _treasuryContract,
        address _auctionContract,
        address _stakingManagerContract,
        address _tnftContract,
        address _bnftContract
    ) external initializer {
        ...
        tnft = TNFT(_tnftContract);
        bnft = BNFT(_bnftContract);

        // in basis points for higher resolution
        stakingRewardsSplit = RewardsSplit({
            treasury: 50_000, // 5 %
            nodeOperator: 50_000, // 5 %
            tnft: 815_625, // 90 % * 29 / 32 ///<----------------- @audit
            bnft: 84_375 // 90 % * 3 / 32  ///<----------------- @audit
        });
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/55_

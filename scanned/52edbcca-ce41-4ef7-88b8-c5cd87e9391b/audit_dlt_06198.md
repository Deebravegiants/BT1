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

According to the "[T-NFT and B-NFT](https://etherfi.gitbook.io/etherfi/ether.fi-whitepaper/technical-documentation#t-nft-and-b-nft)" part in the documentation, we can see the allocation of claimable staking rewards between a T-NFT holder and a B-NFT holder like this:
> The T-NFT and B-NFT represent claims of **30 ETH and 2 ETH**, respectively, for the withdrawn funds upon the validator node's exit. That is, the staker can liquify **93.75%** (= **30/32**) of their staking position. Here, because the staker retains control of the validator key, the B-NFT acts as insurance against slashing as well as a commitment to exit the validator node upon request from the T-NFT holder. 

Based on above,
- a B-NFT holder is supposed to be able to liquify `2 / 32 ETH`, which is **6.25%**.
- a T-NFT holder is supposed to be able to liquify `30 / 32 ETH`, which is **93.75%**.

Since the [10% of the staking rewards would be allocated for a Treasury and a Node Operator](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L121-L122), the remained-allocation of the staking rewards for a T-NFT holder and a B-NFT holder would be 90%. 
Based on it, the calculation of how much staking rewards is allocated for a T-NFT holder and a B-NFT holder is supposed to be like this:
- a B-NFT holder is supposed to be able to liquify `(2 / 32 ETH) * 90%`, which is **5.625%**.
- a T-NFT holder is supposed to be able to liquify `(30 / 32 ETH) * 90%`, which is **84.375%**.

However, within the [`stakingRewardsSplit`-set in the EtherFiNodesManager#`initialize()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L123-L124), the allocation of staking rewards for a B-NFT holder and a T-NFT holder would be like this:
- a B-NFT holder can liquify `(3 / 32 ETH) * 90%`, which is **8.4375%**.
- a T-NFT holder can liquify `(29 / 32 ETH) * 90%`, which is **81.5625%**.

## Impact
This is problematic because this lead to wrong initial allocation of the staking rewards for a B-NFT holder and a T-NFT holder like this:
- a B-NFT holder would receive a **larger amount** of the staking rewards than the **actual amount** of it that the B-NFT holder should receive.
- a T-NFT holder would receive a **smaller amount** of the staking rewards than the **actual amount** of it that the T-NFT holder should receive.

## Recommendation
Within the `stakingRewardsSplit`-set in the EtherFiNodesManager#`initialize()`, consider modifying the initial allocation of the staking rewards for a B-NFT holder and a T-NFT holder like this:
```diff
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
+           tnft: 843_750, // 90 % * 30 / 32
-           tnft: 815_625, // 90 % * 29 / 32
+           bnft: 56_250 // 90 % * 2 / 32
-           bnft: 84_375 // 90 % * 3 / 32
        });
```

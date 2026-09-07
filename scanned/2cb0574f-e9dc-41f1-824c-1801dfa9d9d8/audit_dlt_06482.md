# [M] LM_PC_Staking_v1&LM_PC_KPIRewarder - User can brick both contracts if he is first staker

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-14
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/126
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @EgisSec
**Submission hash (on-chain):** 0xd550ad6931bdc9f1efc508de69e199837236e00ad4e569aed416ef1d775fa619
**Severity:** medium

**Description:**
**Description**\
The issue exists in both contracts and is technically the same, so I grouped them together.

Both `LM_PC_Staking_v1` and `LM_PC_KPIRewarder_v1` have a `stake` function.

```solidity
function stake(uint amount)
        external
        virtual
        nonReentrant
        validAmount(amount)
        //@audit can stake before rewardsEnd and rewardRate is set
    {   
        address sender = _msgSender();

        _stake(sender, amount);

        // transfer funds to LM_PC_Staking_v1
        IERC20(stakingToken).safeTransferFrom(sender, address(this), amount);
    }
```

```solidity
 function stake(uint amount)
        external
        override
        nonReentrant
        validAmount(amount)
    {
        if (stakingQueue.length >= MAX_QUEUE_LENGTH) {
            revert Module__LM_PC_KPIRewarder_v1__StakingQueueIsFull();
        }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/126_

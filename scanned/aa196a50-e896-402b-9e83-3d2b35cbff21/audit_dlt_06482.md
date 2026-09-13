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

        if (amount < minimumStake) {
            revert Module__LM_PC_KPIRewarder_v1__InvalidStakeAmount();
        }

        address sender = _msgSender();

        if (stakingQueueAmounts[sender] == 0) {
            // new stake for queue
            stakingQueue.push(sender);
        }
        stakingQueueAmounts[sender] += amount;
        totalQueuedFunds += amount;

        // transfer funds to LM_PC_Staking_v1
        IERC20(stakingToken).safeTransferFrom(sender, address(this), amount);

        emit StakeEnqueued(sender, amount);
    }
```

In both functions `stake` is of type `uint = uint256`. There are some tokens like [cUSDCv3](https://optimistic.etherscan.io/token/0x2e44e174f7D53F0212823acC11C01A11d58c5bCB?a=0x2a376410fd9e5546bcce9f5bdabeb5b8ad8d09de#code) that have a special case in their transfer logic.

```solidity
function transferInternal(address operator, address src, address dst, address asset, uint amount) internal {
        if (isTransferPaused()) revert Paused();
        if (!hasPermission(src, operator)) revert Unauthorized();
        if (src == dst) revert NoSelfTransfer();

        if (asset == baseToken) {
            if (amount == type(uint256).max) {
                amount = balanceOf(src);
            }
            return transferBase(src, dst, amount);
        } else {
            return transferCollateral(src, dst, asset, safe128(amount));
        }
    }
```

If the amount specified is `type(uint256).max` then the entire balance of `src` will be transfered.

This is in issue in Inverter, as the above `stake` functions use the `amount` passed as is, meaning if `type(uint256).max` is set, then that's how much the code will credit to the user.

This allows for the first depositor in both contracts to completely brick the contracts, as in botch cases if another user stakes,  a value will overflow, reverting the tx.

This is especially problematic if rewards are already sent to the contract, as it will make withdrawing them impossible. The owner will lose 100% of them.

The scenario isn't so uncommon as cUSDCv3 has a market cap of $62m, so it's not a niche token and the protocol states that it doesn't support fee-on transfer, rebsing or ERC777 tokens and cUSDCv3 is neither.

Similar issues:
[Codehawks](https://github.com/solodit/solodit_content/blob/main/reports/Cyfrin/2024-01-24-cyfrin-solidlyV3.md#attacker-can-corrupt-rewardsdistributor-internal-accounting-forcing-lp-token-incentive-deposits-to-revert-for-tokens-like-cusdcv3)
[Sherlock](https://github.com/sherlock-audit/2023-09-Gitcoin-judging/issues/379)

**Attack Scenario**\
1. `LM_PC_KPIRewarder_v1`is deployed and the token is cUSDCv3.
2. The admin pre-sends the reward tokens to the contract.
2. Alice has dust amounts of cUSDv3 calls `stake` with `amount = type(uint256).max`.
3.  `totalQueuedFunds` is now equal to `type(uint256).max` so anyone that calls `stake` will overflow the value and revert the tx.
4. There is no way to forcefully dequeue Alice's stake, so the funds are stuck.

The same scenario happens in `LM_PC_Staking_v1`, `totalSupply` will be set to `type(uint256).max` and no one else can stake after that and the reward tokens will again be stuck.

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

Change `amount` to type `uint128`.

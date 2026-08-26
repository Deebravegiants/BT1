# [M] User won't be able to get back their staked USDC/USDT token if their address is blacklisted in `LM_PC_Staking_v1.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/54
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0xcc5288cac2a3745a964f41e886a1bf16b3c7238ee2fde72e52333d7bd5130de4
**Severity:** medium

**Description:**
**Description**\
`LM_PC_Staking_v1.sol` contract provides a mechanism for users to their tokens to earn rewards. This is done by calling `LM_PC_Staking_v1.stake()` function. When the users wants to get back their staked tokens with rewards, `LM_PC_Staking_v1.unstake()`can be called by users.

Per the discussion with protocol team, its understood that `LM_PC_Staking_v1` admin is free to consider any token as `stakingToken` except FOT/rebasing/callback tokens. 

This issue is specifically for tokens like USDC which has a blacklist() function and it is used to blacklist any address by USDC admin. This can be checked [here](https://optimistic.etherscan.io/address/0xded3b9a8dbedc2f9cb725b55d0e686a81e6d06dc#code)

The contracts will be deployed on Optimism,Polygon, linea.

Consider below scenario to understand the issue better:

1) `LM_PC_Staking_v1` is deployed on Optimism and admin has considered USDC as `stakingToken. 

2) Alice wants to stake her USDC so she calls `LM_PC_Staking_v1.stake()` and transfer the USDC to `LM_PC_Staking_v1` contract. 

```solidity
170        IERC20(stakingToken).safeTransferFrom(sender, address(this), amount);
```

3) After few days/months, Alice decides to unstake the staked tokens i.e to get back USDC from `LM_PC_Staking_v1` so she calls `LM_PC_Staking_v1.unstake()`. Alice finds that her address is blacklisted by USDC.

4) When `LM_PC_Staking_v1` contract ties to transfer the USDC to Alice address:

```solidity
    function unstake(uint amount)
        external
        virtual
        nonReentrant
        validAmount(amount)
    {
@>      address sender = _msgSender();
        // Update rewardValue, updatedTimestamp and earned values
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/54_

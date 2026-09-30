# [M] Lockup-Free WhiteStaking::withdraw()

## Summary
Severity: Medium
Contest weight: 0.4234
Dataset id: 13388
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the Whiteheart protocol will generate and collect settlement fees paid every time when an ATM put option contract is purchased. To encourage the protocol adoption, the protocol has a built-in staking-based incentivizer mechanism as demonstrated in the WhiteStakingUSDC contract.
In order to prevent possible flashloan-assisted sandwich-style arbitrages that may claim the majority of rewards, the staking logic is designed to have a lockup period for staked assets. For each account, the associated lockup period is recorded as [lastBoughtTimestamp[account], lastBoughtTimestamp[account].add(lockupPeriod)].
```solidity
function deposit(uint amount)
    external
    override
{
    lastBoughtTimestamp[msg.sender] = block.timestamp;
    require(amount > 0, "!amount");
    WHITE.safeTransferFrom(msg.sender, address(this), amount);
    _mint(msg.sender, amount);
}

function withdraw(uint amount)
    external
    override
{
    _burn(msg.sender, amount);
    WHITE.safeTransfer(msg.sender, amount);
}
```
However, it comes to our attention that the unstaking function, i.e., withdraw(), does not honor the lockup period, which completely defeat the purpose of the lockup period design. To mitigate, we suggest to use the lockupFree modifier with the withdraw() routine.

## Recommendation
Properly enforce the lastBoughtTimestamp when a staking user attempts to withdraw the staked assets.

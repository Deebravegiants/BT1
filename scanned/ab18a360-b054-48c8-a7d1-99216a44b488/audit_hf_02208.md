# [M] Non-Functional Lockup Periods in HegicStaking

## Summary
Severity: Medium
Contest weight: 0.6936
Dataset id: 12223
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the Hegic protocol will generate and collect settlement fees (in ETH and WBTC) paid every
time when a hegic option contract is purchased. The HEGIC token holders can stake their tokens to
receive pro-rata staking rewards. For example, if there will be 10 active staking lots, each of them
will be receiving 10% of rewards; and if there will be 100 active staking lots, each of them will be
receiving 1% of rewards.
The staking logic is implemented in two contracts: HegicStakingETH and HegicStakingWBTC. As the
names indicate, they are pool-specific. In order to prevent possible flashloan-assisted front-running
attacks that may claim the majority of rewards, the staking logic is designed to have a lockup period
for staked assets. For each account, the associated lockup period is recorded as [lastBoughtTimestamp
[account], lastBoughtTimestamp[account].add(lockupPeriod)].
```solidity
function buy(uint amount) external override {
    require(amount > 0, "Amount is zero");
    require(totalSupply() + amount <= MAX_SUPPLY);
    _mint(msg.sender, amount);
    HEGIC.safeTransferFrom(msg.sender, address(this), amount.mul(LOT_PRICE));
}
```
However, it comes to our attention that the staking function, i.e., buy(), does not record the
lastBoughtTimestamp of the buyer. As a result, the protocol keeps the default lastBoughtTimestamp of 0
for the buyer. When any transfer() or transferFrom() action occurs, the lockup verification routine,
i.e., _beforeTokenTransfer(), always gives a green light even when the transferred staking pool tokens
are just bought! In other words, despite the fact the receiver may have explicitly requested for not
accepting any funds in the lockup period: _revertTransfersInLockUpPeriod[receiver] == true (line
108), the transfer will not be blocked.
```solidity
function _beforeTokenTransfer(address from, address to, uint256) internal override {
    if (from != address(0)) saveProfit(from);
    if (to != address(0)) saveProfit(to);
    if (lastBoughtTimestamp[from].add(lockupPeriod) > block.timestamp && lastBoughtTimestamp[from] > lastBoughtTimestamp[to])
        require(
            !_revertTransfersInLockUpPeriod[to],
            "the recipient does not accept blocked funds"
        );
    lastBoughtTimestamp[to] = lastBoughtTimestamp[from];
}
```
Similarly, since the protocol always keeps the default _beforeTokenTransfer() value for any ac-
count, the lockupFree modifier (require(lastBoughtTimestamp[msg.sender].add(lockupPeriod)<= block
.timestamp)) is always satisfied, meaning any stakers can immediately sell without being locked.
```solidity
function sell(uint amount) external override lockupFree {
    _burn(msg.sender, amount);
    HEGIC.safeTransfer(msg.sender, amount.mul(LOT_PRICE));
}
```

## Recommendation
Properly record the lastBoughtTimestamp when a HEGIC holder stakes the
assets as follows:
```solidity
function buy(uint amount) external override {
    require(amount > 0, "Amount is zero");
    require(totalSupply() + amount <= MAX_SUPPLY);
    lastBoughtTimestamp[msg.sender] = block.timestamp;
    _mint(msg.sender, amount);
    HEGIC.safeTransferFrom(msg.sender, address(this), amount.mul(LOT_PRICE));
}
```

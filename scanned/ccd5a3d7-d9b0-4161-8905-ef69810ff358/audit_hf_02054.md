# [H] Possible CooldownTimestamp Manipulation

## Summary
Severity: High
Contest weight: 0.6356
Dataset id: 11684
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the Augmented Finance protocol will reward participating users if they stake their tokens to receive pro-rata staking rewards. In order to prevent possible flashloan-assisted front-running attacks that may claim the majority of rewards, the staking logic is designed to have a cooldown period for staked assets. For each account, the associated cooldown period is recorded internally as _stakersCooldowns. When there is a stake operation, the staking user's cooldown timestamp is properly updated. When the pool token is transferred, the receiver's cooldown timestamp will also be updated. The new cooldown timestamp is calculated in the following getNextCooldown() routine.
```solidity
function getNextCooldown(
    uint32 fromCooldownPeriod,
    uint256 amountToReceive,
    address toAddress,
    uint256 toBalance
) public returns (uint32) {
    uint32 toCooldownPeriod = _stakersCooldowns[toAddress];
    if (toCooldownPeriod == 0) {
        return 0;
    }
    uint256 minimalValidCooldown = block.timestamp.sub(_cooldownPeriod).sub(_unstakePeriod);
    if (minimalValidCooldown > toCooldownPeriod) {
        toCooldownPeriod = 0;
    } else {
        if (minimalValidCooldown > fromCooldownPeriod) {
            fromCooldownPeriod = uint32(block.timestamp);
        }
        if (fromCooldownPeriod < toCooldownPeriod) {
            return toCooldownPeriod;
        } else {
            toCooldownPeriod = uint32(
                (amountToReceive.mul(fromCooldownPeriod).add(toBalance.mul(toCooldownPeriod)))
                .div(amountToReceive.add(toBalance))
            );
            _stakersCooldowns[toAddress] = toCooldownPeriod;
            return toCooldownPeriod;
        }
    }
}
```
If a staking user has not passed the cooldown timestamp, the staked funds will be locked inside the staking contract. It comes to our attention that this above getNextCooldown() routine is public, which means any one is able to call it. Also, it surprisingly updates the given toAddress's cooldown timestamp directly. In other words, a malicious actor may simply lock another victim's staking funds inside the contract.

## Recommendation
Restrict the getNextCooldown() call or make the function view-only.

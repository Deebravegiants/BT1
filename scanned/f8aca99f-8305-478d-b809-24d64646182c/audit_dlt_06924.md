# [H] Permanent freeze of funds

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-stakehouse
Published: 2022-11-18
Source: https://github.com/code-423n4/2022-11-stakehouse-findings/issues/176
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-stakehouse/blob/4b6828e9c807f2f7c569e6d721ca1289f7cf7112/contracts/liquid-staking/LiquidStakingManager.sol#L326
https://github.com/code-423n4/2022-11-stakehouse/blob/4b6828e9c807f2f7c569e6d721ca1289f7cf7112/contracts/liquid-staking/LiquidStakingManager.sol#L934
https://github.com/code-423n4/2022-11-stakehouse/blob/4b6828e9c807f2f7c569e6d721ca1289f7cf7112/contracts/liquid-staking/LiquidStakingManager.sol#L524


# Vulnerability details

## Impact

* Permanent freeze of funds - users who deposited ETH for staking will not be able to receive their funds, rewards or rotate to another token. The protocol becomes insolvent, it cannot pay anything to the users.
* Protocol's LifecycleStatus state machine is broken 

Other impacts:
* Users deposit funds to an unstakable validator (node runner has already took out his funds)

Impact is also on the Giant Pools that give liquidity to the vaults.

A competitor or malicious actor can cause bad PR for the protocol by causing permanent freeze of user funds at LSD stakehouse.
## Proof of Concept

There are two main bugs that cause the above impact:
1. Reentrancy bug in `withdrawETHForKnot` function in `LiquidStakingManager.sol`
2. Improper balance check in `LiquidStakingManager.sol` for deposited node runner funds. 

For easier reading and understanding, please follow the bellow full attack flow diagram when reading through the explanation.
```
┌───────────┐               ┌───────────┐            ┌───────────┐              ┌───────────┐
│           │               │           │            │           │              │           │
│Node Runner│               │LSD Manager│            │   Vaults  │              │   Users   │
│           │               │           │            │           │              │           │
└─────┬─────┘               └─────┬─────┘            └─────┬─────┘              └─────┬─────┘
      │                           │                        │                          │
      │   Register BLS Key #1     │                        │                          │
      ├──────────────────────────►│                        │                          │
      │                           │                        │                          │
      │   Register BLS Key #1     │                        │                          │
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-stakehouse-findings/issues/176_

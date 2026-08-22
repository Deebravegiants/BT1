# [H] Initialization functions can be front-run with malicious values

## Summary
Severity: High
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-23
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/67
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Most contracts have public visibility initialization functions that can be front-run, allowing an attacker to incorrectly initialize the contracts. Due to the use of the delegatecall proxy pattern, PrizePool/YieldSourcePrizePool/StakePrizePool, ControlledToken/Ticket and yield source contracts ATokenYieldSource/IdleYieldSource/YearnV2YieldSource among others cannot be initialized with a constructor, and have initializer functions. 

It is not clear (outside scope of current contracts) if/how the deployment of these contracts handles initializations to prevent front-running.

Impact: All these functions can be front-run by an attacker, allowing them to initialize the contracts with malicious values. Also, if not initializations are not done atomically with creation, all public/external functions can be accessed before initialization because there are no checks to confirm initializations in those functions.

## Proof of Concept

Reference: See similar High-severity Finding 9 of Trail of Bits audit of Advanced Blockchain: https://github.com/trailofbits/publications/blob/master/reviews/AdvancedBlockchain.pdf and Finding 12 from Trail of Bits audit of Hermez Network https://github.com/trailofbits/publications/blob/master/reviews/hermez.pdf

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L217-L224

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/YieldSourcePrizePool.sol#L24-L32

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/StakePrizePool.sol#L20-L28

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/ControlledToken.sol#L22-L30

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/Ticket.sol#L24-L33

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/yield-source/ATokenYieldSource.sol#L84-L94

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/yield-source/IdleYieldSource.sol#L56-L58

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/yield-source/YearnV2YieldSource.sol#L66-L71

## Tools Used

Manual Analysis

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/67_

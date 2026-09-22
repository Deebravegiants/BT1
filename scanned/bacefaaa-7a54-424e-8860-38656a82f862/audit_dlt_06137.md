# [H] reorg attack due to usage of `clone`

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-25
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/88
Type: hats-finding

## Details
**Github username:** @Nabeel-javaid
**Submission hash (on-chain):** 0x4f27574e5d5b09674cf8e4867b6f44650ca447dca1fb8aaf8726484cbbb57c79
**Severity:** high

**Description:**
**Description**\
An issue: an attacker can steal funds via a reorg attack if a contract is funded within a few blocks of being created inside a factory. 

**Attack Scenario**\

Here is the effected code

https://github.com/stakewise/v3-core/blob/c82fc57d013a19967576f683c5e41900cbdd0e67/contracts/misc/RewardSplitterFactory.sol#L29

kind of similar vulnerability here

https://code4rena.com/reports/2023-01-rabbithole#m-01-questfactory-is-suspicious-of-the-reorg-attack

**Recommendation**

use cloneDeterministic as cloneDeterministic uses the opcode and a `salt` to deterministically deploy the clone. Using the same `implementation` and `salt` multiple times will revert since the clones cannot be deployed twice at the same address.
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/proxy/Clones.sol

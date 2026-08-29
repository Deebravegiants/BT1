# [M] Phantom overflows can lead to unexpected reverts

## Summary
Severity: Medium
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-17
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/42
Type: hats-finding

## Details
**Github username:** @cpp-phoenix
**Twitter username:** aarambh_audits
**Submission hash (on-chain):** 0x28c86afc94a393848aa94331bae67a0797e44cf9b289ef6dd3d668db136c4363
**Severity:** medium

**Description:**
**Description**\
When two number with decimals are multiplied, they are divided with decimals afterwards to avoid precision loss. Unchecked multiplication can lead to phantom overflows i.e., multiplication and division where an intermediate value overflows 256 bits.
 
**Attack Scenario**\
There are mutiple instances in the code where the multiplication between two numbers with decimal points can lead to phantom overflows. Mentioned below are the places where phantom overflow can happen.

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L231

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L510

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L561

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L587

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L603

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L684

https://github.com/PossumLabsCrypto/Portals/blob/5e1855411121ccd883f15c0d3c8d2fd9fc1d8e4c/contracts/Portal.sol#L881

**Recommendation**\
This can be avoided by using Uniswap FullMath library which facilitates multiplication and division that can have overflow of an intermediate value without any loss of precision. 

https://docs.uniswap.org/contracts/v3/reference/core/libraries/FullMath

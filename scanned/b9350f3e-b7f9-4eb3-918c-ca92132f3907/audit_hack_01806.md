# [M] Overflow/underflow protection

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Having overflow/underflow vulnerabilities is very common for smart contracts. It is usually mitigated by using `SafeMath` or using solidity version ^0.8 (after solidity 0.8 arithmetical operations already have default overflow/underflow protection).

In this code, many arithmetical operations are used without the 'safe' version. The reasoning behind it is that all the values are derived from the actual ETH values, so they can't overflow. 

On the other hand, some operations can't be checked for overflow/underflow without going much deeper into the codebase that is out of scope:


**code/contracts/genesis/GenesisGroup.sol:L131**
```solidity
uint totalGenesisTribe = tribeBalance() - totalCommittedTribe;
```

#### Recommendation

In our opinion, it is still safer to have these operations in a safe mode. So we recommend using `SafeMath` or solidity version ^0.8 compiler.

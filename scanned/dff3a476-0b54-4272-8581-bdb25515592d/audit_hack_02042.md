# [M] 6.1 Unauthorized Top Ups

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

With the current design, anybody can call topUp on any operator (in Kepp, Nu and T). This could lead to
KEEP or NU staked in legacy contract, that the owner may not want to be staked on the new staking
contract, ending staked on the new contract.

On Nu this might lead to trolling by calling topUpNu after a user send an unstakeNu transaction and
blocking the Nu withdraw through:

```
1.X calls unstakeNu
2.Y calls topUpNu on X
```
```
3.X tries to withdraw from NU legacy staking contract, but it fails because there is still an amount
of NU accounted in the new staking contract
```
With Keep the issue is more severe as non-malicious behavior could be slashed with a sandwich attack
like follows:

```
1.Someone wants to unstake keep and calls "unstakeKeep"
```
```
2.The user sends the tx for the Keep legacy contract to "undelegate"
3.This tx lands in the men pool and someone front runs it by calling "topUpKeep"
4.The undelegate is mined after the top up
5.The attacker calls the notify keep discrepancy function to slash
```

Code corrected :

A modifier has been added to all three top up functions to restrict the access only to owner and operator.

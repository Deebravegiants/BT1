# [M] Element and weight correlation when `numElements` is multiple of 31

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/56
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/1192a55963c92fb4bd9ca8e0453c96af09731235/src/FighterFarm.sol#L516-L517


# Vulnerability details



## Impact
When `numElements` is a multiple of 31 the DNA only generates 1/31 of all intended combinations of `element` and `weight`.

## Proof of Concept
`numElements` maps to a uint8, i.e up to 255. 
In `FighterFarm._createFighterBase()` `element` and `weight` are set as
```solidity
uint256 element = dna % numElements[generation[fighterType]];
uint256 weight = dna % 31 + 65;
```
This means that if `numElements[generation[fighterType]]` is multiple of `31`, say `k*31` then only `k*31` different combinations are possible instead of `k*31 * 31`, since `(n + k*31) % (k*31) == (n + k*31) % 31`.

## Recommended Mitigation Steps
Divide by the first mod to extract multiple smaller random numbers from one big random number.
```solidity
uint256 weight = dna % 31 + 65;
dna = dna/31;
uint256 element = dna % numElements[generation[fighterType]];
```


## Assessed type

Math

# [M] Voter.replaceFactory()and Voter.addFactory()

## Summary
Severity: Medium
Contest weight: 0.5492
Dataset id: 23111
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Voter.replaceFactory() and Voter.addFactory() functions are broken due to invalid validation.
1. In the addFactory() function, the line require(!isFactory[_pairFactory], 'factory true'); is missing.
2. In the replaceFactory() function, the isFactory and isGaugeFactory checks are incorrect:
```solidity
require(isFactory[_pairFactory], 'factory false'); // <=== should be !isFactory
require(isGaugeFactory[_gaugeFactory], 'g.fact false'); // <=== should be !isGaugeFactory
```
These issues lead to the invariant being broken, allowing multiple instances of a factory or gauge to be pushed to the factories and gaugeFactories arrays. Broken code. DoS when calling Voter.createGauge().

## Recommendation
1. Add the require(!isFactory[_pairFactory], 'factory true'); validation to the addFactory() function.
2. Fix the checks in the replaceFactory() function:
```solidity
require(!isFactory[_pairFactory], 'factory true');
require(!isGaugeFactory[_gaugeFactory], 'g.fact true');
```

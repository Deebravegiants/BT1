# [H] H-01 | Invalid Portion Burned

## Summary
Severity: High
Contest weight: 0.0990
Dataset id: 21508
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the reheat function the reserveSize is computed with a denominator of 100e18, however the minPortion and maxPortion are assigned to as .05 ether and .15 ether respectively in the constructor. The comment on line 150 indicates that the portion ought to be 15% rather than 0.15%, therefore the portion is a factor of 100x smaller than it ought to be.

## Recommendation
Use a denominator of 1e18 rather than 100e18.

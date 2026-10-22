# [M] EDPU-1 | Invalid Deposit Price Impact For Homogenous Markets

## Summary
Severity: Medium
Contest weight: 0.0989
Dataset id: 18858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When depositing, swap impact is calculated for the longTokenUsd and shortTokenUsd being deposited. However in the case of markets where longToken == shortToken, all the value being deposited will be in the longTokenUsd. The market will always be considered balanced to begin with since the poolAmount is simply divided by two for both sides. Therefore every deposit will receive negative impact because each deposit is treated as if it is adding all its value to the long side and therefore unbalancing the pool.

## Proof of Concept
https://github.com/GuardianAudits/GMX-6/blob/main/test/guardian/EDU-1.ts

## Recommendation
Skip price impact calculations when depositing into markets where longToken == shortToken.

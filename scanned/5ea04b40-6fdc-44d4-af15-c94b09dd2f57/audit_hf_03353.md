# [M] CLC-1 | boundedSub Can Underﬂow

## Summary
Severity: Medium
Contest weight: 0.0583
Dataset id: 18204
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The boundedSub function does not correctly prevent underflow. For example, boundedSub(type(int256).min, 1) causes an underflow and reverts because the condition check if (a < 0 && b <= type(int256).min - a) is incorrect. This poses inherent risk for the future use of boundedSub in this codebase and others that may adopt it.

## Recommendation
Replace with if (a < 0 && b >= a - type(int256).min) or if (a < 0 && -b <= type(int256).min - a).

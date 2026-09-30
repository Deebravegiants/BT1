# [M] M-4 Admin can set non-zero pluginConfig in pool with zero plugin

## Summary
Severity: Medium
Contest weight: 0.0639
Dataset id: 2865
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AlgebraPool.sol#L431 The Administrator can set a non-zero value for pluginConfig while setting the plugin to zero. Such a configuration can potentially trigger reverts in pool functions. This issue is classified as medium, as the combination of a non-zero pluginConfig with a zero plugin can disrupt certain functionalities of the pool.

## Recommendation
In order to ensure consistency and prevent potential disruptions, we recommend including a conditional check: if (plugin == 0) require(pluginConfig == 0);. 2.4 Low

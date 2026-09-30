# [M] M-2 Missing ﬂags validation in new pluginConfig

## Summary
Severity: Medium
Contest weight: 0.0712
Dataset id: 2887
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no validation of ﬂags in new pluginConfig set with AlgebraPool.setPluginConfig(). This can lead to the invocation of hooks that will constantly revert. E.g. BEFOREFLASHFLAG, AFTERFLASHFLAG, AFTERSWAPFLAG (without currently connected incentive) can be switched on.
This issue has a MEDIUM severity since it can partially or fully stop the pool until pluginConfig is corrected.

## Recommendation
We recommend moving all interaction with pluginConfig to the plugin contract. Any modiﬁcation of pluginConfig should consider the current version and state of the plugin.

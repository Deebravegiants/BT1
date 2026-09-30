# [M] send() doesnt work on zkSync

## Summary
Severity: Medium
Contest weight: 0.0503
Dataset id: 13554
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
send() and transfer() don't work on zkSync due to forwarding fixed gas (2300). Moreover, their use is discouraged on other chains as gas costs can change. See these resources: • https://twitter.com/zksync/status/1644139364270878720 • https://consensys.io/diligence/blog/2019/09/stop-using-soliditys-transfer-now/

## Recommendation
Use the low-level call:

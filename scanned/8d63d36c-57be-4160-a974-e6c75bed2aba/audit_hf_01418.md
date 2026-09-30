# [H] H-1 TheControllerV2 implementation can be destroyed by an attacker

## Summary
Severity: High
Contest weight: 0.1211
Dataset id: 7310
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ControllerV2 implementation code is vulnerable to a direct call of initialize. Since initialize executes delegatecall to an arbitrary address, an attacker can destroy the Controller's implementation contract, thus freezing the entire system until manual intervention by the proxy administrator occurs. This is accordingly rated as high in severity.

## Recommendation
Although this vulnerability can be hotﬁxed through an accurate deployment process, we recommend addressing it at the smart contract code level by preventing direct calls to initialize against the implementation address.

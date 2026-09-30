# [M] M-17 | Single Token Pod Assumption

## Summary
Severity: Medium
Contest weight: 0.1109
Dataset id: 22187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When getting price from the oracle, if the base token is a pod, _getBaseTokenInClPool is called. There it gets all assets from the pod and assumes the first token in the array is the base token. However, pods were designed to be multi-asset and able to be created permissionlessly. Therefore, if the first asset is not the intended base token, then serious integration issues would occur. Furthermore in the function _debondFromSelfLendingPod, an assumption is made that the selfLendingPod has only one token. If ever this assumption is broken, there would be integration errors with FraxlendPair and a possibility of stuck tokens in LeverageManager after debonding.

## Recommendation
In the constructor, similar to how UNDERLYING_TKN is defined, store the intended underlying token for the base (pod). Furthermore, consider handling the case where a SelfLendingPod has multiple tokens.

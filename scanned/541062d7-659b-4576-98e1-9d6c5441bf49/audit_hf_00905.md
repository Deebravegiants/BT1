# [M] createCommonProjectIDAndDeployment

## Summary
Severity: Medium
Contest weight: 0.1155
Dataset id: 2669
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
createCommonProjectIDAndDeploymentRequest() is called by createAgent(), in which the user pays fees to create an agent. The index is supposed to protect the user from overwritting a requestId with the same requestId but different serverURL. However, it is hardcoded to 0.
In BlueprintCore:373, index is 0.
Internal Pre-conditions
None.
External Pre-conditions
None.
Attack Path
1. User creates an agent for a certain projectId, base64Proposal, server url.
2. User creates an agent (at the same block) with the same projectId, base64Proposal but different server url.
3. First request is overwritten.
First request is overwritten and one of them will not be finalized as submitProofOfDeployment() and submitDeploymentRequest() can only be called once as only one of them will go through.

## Recommendation
Index should be increment in a user mapping.

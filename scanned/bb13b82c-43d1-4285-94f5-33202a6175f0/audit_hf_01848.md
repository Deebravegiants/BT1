# [C] C-1 The governance adapter is not protected

## Summary
Severity: Critical
Contest weight: 0.1466
Dataset id: 10270
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current implementation, flexGovernanceAdapater allows any user to call any function in the adapter, which can be exploited by a malicious user to create a proposal to transfer all tokens to an incorrect address. Considering that only implants should be able to call the adapter to pass speciﬁc calls to governance, this issue is severe and must be ﬁxed before deployment:  
• flexGovernanceAdapater.sol#L34  
• flexGovernanceAdapater.sol#L45  
• flexGovernanceAdapater.sol#L56  
• flexGovernanceAdapater.sol#L64.

## Recommendation
We recommend adding a modiﬁer that will restrict method calls to only whitelisted addresses.

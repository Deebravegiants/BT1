# [M] Users can't request to withdraw at any time like the docs say

## Summary
Severity: Medium
Contest weight: 0.0910
Dataset id: 16246
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Vault documentation page, we can see the following answer to the FAQ "How do I withdraw?": You can withdraw your LYX and rewards at any time. But that is not 100% true. There is a pause functionality controlled by the owner present in the contract. Meaning if there is a malicious or compromised owner, he can pause the contract which will affect exactly the withdraw function (other ones as well) and it will become not callable due to the whenNotPaused modifier in this function.

## Recommendation
While this is a scenario that requires a special factor (malicious/compromised owner or an emergency situation), there is still a chance for that to occur. For that reason, we suggest not to guarantee that users will be able to withdraw their rewards at any time.

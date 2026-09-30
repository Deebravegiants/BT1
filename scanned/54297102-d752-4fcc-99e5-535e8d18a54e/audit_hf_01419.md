# [H] H-3 Funds may freeze on the TimeLock if the beneﬁciary does not implement

## Summary
Severity: High
Contest weight: 0.1257
Dataset id: 7312
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Assets from the TimeLock can only be claimed by their respective beneﬁciaries via calling the claim function. However, if the beneﬁciary is an immutable smart contract with no ability to invoke claim against the TimeLock, the locked assets become inaccessible to the beneﬁciary. Given that some accounts will be unable to access their assets until the manual intervention of the smart contract owner, this issue is rated as high in severity.

## Recommendation
We recommend allowing any account to invoke the claim.

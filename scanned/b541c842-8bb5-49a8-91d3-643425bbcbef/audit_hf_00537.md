# [M] M-11 | Insufficient Return Data Length Options

## Summary
Severity: Medium
Contest weight: 0.1342
Dataset id: 1995
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the triggerMetadataRead and triggerOwnershipUpdate functions there is no enforcement of the expected returndata length for the read request. The expected returndata length must be speciﬁed so that the executor can be adequately compensated for executing the lzReceive function once the message has been veriﬁed. If users call the triggerMetadataRead and triggerOwnershipUpdate functions with extra options including the correct return data size then the executor will not execute the lzReceive function upon DVN veriﬁcation and users will have to manually execute the message through the endpoint. Furthermore the return data size cannot be enforced at the enforced options level since it varies based upon the query being made.

## Recommendation
For the Beacon contract Implement the use of the getReadOptions function at the Beacon contract level instead of including this in the NFTShadow contract so that all read requests are properly conﬁgured, not just those coming through the NFTShadow contract. For the MetaDataReadRenderer only expose the triggerMetadataRead function through the NFTShadow collection contract and enforce that sufficient expected return data is speciﬁed in the options for each collection's respective tokenUri length.

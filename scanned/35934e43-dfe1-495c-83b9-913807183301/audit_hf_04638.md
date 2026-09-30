# [M] M-02 | contractURI Metadata Is Not Queryable From ERC721 Mirror

## Summary
Severity: Medium
Contest weight: 0.0764
Dataset id: 22377
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Token contract implements a contractURI function which is intended to include collection level metadata about the ERC721 counterpart of the DN404 pair. However, unlike the tokenURI, the contractURI cannot be queried from the DN404Mirror contract and therefore this metadata is not available for integrators who would query the ERC721 compatible contract for it.

## Recommendation
Create a contract which inherits from the DN404Mirror contract and adds a contractURI function which uses _readString to query the DN404 base contract, similar to the tokenURI function. Then override the dn404Fallback function to add the corresponding selector functionality for a _contractURI function.

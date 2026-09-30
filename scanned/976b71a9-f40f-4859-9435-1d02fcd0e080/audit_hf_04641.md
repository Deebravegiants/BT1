# [M] M-05 | Contract URI Does Not Conform To ERC-7572

## Summary
Severity: Medium
Contest weight: 0.0963
Dataset id: 22380
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In contractURI, the field for external_url should be named external_link instead to conform with ERC-7572 (https://eips.ethereum.org/EIPS/eip-7572). Additionally, ERC-7572 requires an event ContractURIUpdated, which is currently not implemented. This is also the standard that Opensea uses, see [metadata](https://docs.opensea.io/docs/contract-level-metadata). Not adhering to ERC-7572 could result in improper display of information on secondary marketplaces like Opensea where NFTs are traded. It should be noted however that in tokenURI, external_url is the correct naming.

## Recommendation
Rename the media field from external_url to external_link. Create a separate update function for contractURI and emit the event ContractURIUpdated.

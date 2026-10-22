# [M] M-02 | There Is No Function For triggerMetadataRead

## Summary
Severity: Medium
Contest weight: 0.0685
Dataset id: 2010
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MetadataReadRenderer has a function to update the metadata for NFTs on different chains. Where the main function - triggerMetadataRead must be called by the NFTShadow contract to invoke the change, as it gets the baseCollectionAddress from IBeacon(beacon).shadowToBase(msg.sender). Meaning that msg.sender must be NFTShadow. However the NFTShadow lacks a method which invokes triggerMetadataRead.

## Recommendation
Add a function inside NFTShadow that can invoke triggerMetadataRead, make sure it has onlyOwner

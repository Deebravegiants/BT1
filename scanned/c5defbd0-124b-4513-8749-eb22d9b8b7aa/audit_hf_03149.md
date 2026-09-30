# [H] Incorrect translation of require checks to revert

## Summary
Severity: High
Contest weight: 0.1991
Dataset id: 17681
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are a number of instances where the require checks in the original libraries were incorrectly translated to revert conditions.
One of the changes to the utils libraries from the referenced ones were the use of custom errors instead of require statements. This means that conditions and checks have to be inverted. For instance, require(x==0) is to be replaced with if(x!=0)revertCustomError().
One of these conditions was inverted incorrectly. The original statement require(x.length>0); should have been converted to if(x.length==0)revertCustomError(), but was incorrectly converted to if(x.length!=0)revertCustomError() instead.
Broken functionality.

## Recommendation
- if (compact.length != 0)
+ if (compact.length == 0)
    revert MerklePatriciaProofVerifier__decodeNibbles_compactIsZero();
- if (compact.length != 0)
+ if (compact.length == 0)
    revert MerklePatriciaProofVerifier__merklePatriciaCompactDecode_compactIsZero();
- if (item.len != 0) revert RLPReader__toBytes_invalidLen();
+ if (item.len == 0) revert RLPReader__toBytes_invalidLen();

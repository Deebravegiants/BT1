# [C] BLS Signature "Malleability"

## Summary
Severity: Critical
Chain: Filecoin
Component: filecoin-project/lotus
CVE: CVE-2021-21405
Published: 2021-04-15
Source: https://github.com/filecoin-project/lotus/security/advisories/GHSA-4g52-pqcj-phvh
Type: github-advisory

## Details
### Impact

1. BLS signature validation in lotus uses blst library method VerifyCompressed. This method accepts signatures in 2 forms: "serialized", and "compressed", meaning that BLS signatures can be provided as either of 2 unique byte arrays.
2. Lotus block validation functions perform a uniqueness check on provided blocks. Two blocks are considered distinct if the CIDs of their blockheader do not match. The CID method for blockheader includes the BlockSig of the block.

The result of these issues is that it would be possible to punish miners for valid blocks, as there are two different valid block CIDs available for each block, even though this must be unique.

### Patches

By switching from the go based `blst` bindings over to the bindings in `filecoin-ffi`, the code paths now ensure that all signatures are compressed by size and the way they are deserialized.
This happened in https://github.com/filecoin-project/lotus/pull/5393


### References

- Original POC: https://gist.github.com/wadeAlexC/2490d522e81a796af9efcad1686e6754

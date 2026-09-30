# [M] M-03 | Release Stuck On Zero Address Beneficiary

## Summary
Severity: Medium
Contest weight: 0.0856
Dataset id: 1987
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the releaseOnEid function there is no validation that the beneficiary address is not the zero address. Therefore a layerzero message can be sent with the beneficiary set as the zero address. The execution of this message will perpetually fail as all attempts to execute the executeMessage function will revert as the Solady ERC721 library does not support mints or transfers to the zero address. Therefore the Shadow NFTs and base collection NFT will remain locked on all chains with this message stuck in perpetuity.

## Recommendation
In the releaseOnEid function validate that the beneficiary address is not the zero address.

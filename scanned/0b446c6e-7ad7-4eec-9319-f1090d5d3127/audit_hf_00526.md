# [M] M-02 | _checkOnERC721Received Bool Is Not Checked

## Summary
Severity: Medium
Contest weight: 0.0543
Dataset id: 1984
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While creating a position in the liquidity or trading modules, _checkOnERC721Received function is called and then the position NFT is minted. However, _checkOnERC721Received does not revert on failure but only returns false. Return value is not checked and positions can be minted to contracts that can't hold NFTs.

## Recommendation
Check the return value of the function before continuing.

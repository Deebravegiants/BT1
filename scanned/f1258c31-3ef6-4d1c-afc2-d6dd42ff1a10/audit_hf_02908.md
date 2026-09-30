# [M] UF-4 | Mint Failure

## Summary
Severity: Medium
Contest weight: 0.0478
Dataset id: 16218
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In publicMint, when performing _earnTo = random() % (_tokenIdCounter.current() +1), there is a possibility _earnTo is equivalent to _tokenIdCounter.current() which yields a tokenID for a token that does not exist yet. Therefore, the subsequent call to ownerOf will fail and the mint will revert.

## Recommendation
Perform random() % _tokenIdCounter.current().

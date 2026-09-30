# [M] M-05 | Borrowers Exposed To Gas Grieﬁng

## Summary
Severity: Medium
Contest weight: 0.0780
Dataset id: 20845
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the initializeNewLoan function a promissoryNote is minted to the lender using the INFTYERC721V1.mint function, which relies on safeMint. As a result if the lender address is home to a contract, the onERC721Received function will be invoked at that address. The contract at the lender address may have malicious logic implemented for the onERC721Received function to waste the borrower’s gas, causing a loss of native tokens for the user.

## Recommendation
Consider using _mint rather than _safeMint for the mint implementation in the NFTYERC721V1 contract so that borrowers cannot be exposed to gas grieﬁng.

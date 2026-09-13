# [M] Potential reentrancy in safeTransferFrom functions

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L444
Type: audit-issue

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Reentrancy possible from onERC721Received implementation of a malicious contract at _to address. But it doesn’t look like this cannot be exploited here because there are no state effects after the external interaction (i.e. CEI pattern holds). 

Consider adding a reentrancy guard to the safeTransferFrom functions as a safety precaution in case any other functionality is added later which might make this exploitable. 

Reference: The Hashmasks NFT had an exploitable vulnerability with this same vector. See https://thehashmasks.medium.com/hashmask-art-sale-bug-report-13ccd66b55d7.

## Proof of Concept


https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L444

https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L253-L255

https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L257-L259


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add a reentrancy guard to the safeTransferFrom functions.

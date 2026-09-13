# [M] Conviction score is not updated during tokenization if funds are locked

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-26
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/27
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The _updateConvictionScore() on Line284 of tokenizeConviction() is only called if user specifies zero locked funds. This leads to loss of accounting of user’s conviction score for tokenization (since the last update for user) if non-zero amount of FSDs are specified for locking.

## Proof of Concept

Alice receives FSDs and holds for 100 days but forgets to call updateConvictionScore() during this period. When Alice tries to tokenize her conviction score into a NFT, and specifies locking of 10 FSD tokens, she loses accounting for the prior 100 days of conviction and her NFT will not reflect this updated score. 

Even if Alice has called updateConvictionScore() earlier, if she does not call it just before tokenizing it to a NFT (while locking non-zero FSD tokens), the last window of unaccounted conviction score (conviction deltas) is not captured in NFT tokenization leading to an effective loss of accrued fund benefits for Alice and the buyer of that NFT.

https://github.com/code-423n4/2021-05-FairSide/blob/3e9f6d40f70feb67743bdc70d7db9f5e3a1c3c96/contracts/dependencies/ERC20ConvictionScore.sol#L284

https://github.com/code-423n4/2021-05-FairSide/blob/3e9f6d40f70feb67743bdc70d7db9f5e3a1c3c96/contracts/dependencies/ERC20ConvictionScore.sol#L280-L310

## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Updating conviction score should be done during tokenization to capture the latest conviction score irrespective of whether FSDs are being locked or not. Move _updateConvictionScore() outside the else body between Line283-Line285 of ERC20ConvictionScore.sol.

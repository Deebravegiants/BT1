# [M] `PrizePool.awardExternalERC721`

## Summary
Severity: Medium
Contest weight: 0.1056
Dataset id: 1062
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `awardExternalERC721()` function uses solidity’s try and catch statement to ensure a single tokenId cannot deny function execution. If the try statement fails, an `ErrorAwardingExternalERC721` event is emitted with the relevant error, however, the failed tokenId is not removed from the list of tokenIds emitted at the end of function execution. As a result, the `AwardedExternalERC721` is emitted with the entire list of tokenIds, regardless of failure. An off-chain script or user could therefore be tricked into thinking an ERC721 tokenId was successfully awarded.

## Recommendation
Consider emitting only successfully transferred tokenIds in the `AwardedExternalERC721` event.

PR: <https://github.com/pooltogether/v4-core/pull/246>

The sponsor acknowledged and mitigated by actively managing a list of `_awardedTokenIds` to keep track of the tokens that didn’t go through the `catch` part of the error handling

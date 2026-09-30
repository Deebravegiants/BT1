# [M] _validateCommitment fails for approved op-

## Summary
Severity: Medium
Contest weight: 0.1231
Dataset id: 17732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a collateral token owner approves another user as an operator for all their tokens (rather than just for a given token), the validation check in _validateCommitment() will fail. another user: • Approve them to take actions with a given token (approve()) • Approve them as an "operator" for all your owned tokens (setApprovalForAll()) However, when the _validateCommitment() function checks that the token is owned or approved by msg.sender, it does not accept those who are set as operators. if (msg.sender != holder) { require(msg.sender == operator, "invalid request"); } Approved operators of collateral tokens will be rejected from taking actions with those tokens.

## Recommendation
Include an additional check to confirm whether the msg.sender is approved as an operator on the token: address holder = ERC721(COLLATERAL_TOKEN()).ownerOf(collateralId); address approved = ERC721(COLLATERAL_TOKEN()).getApproved(collateralId); address operator = ERC721(COLLATERAL_TOKEN()).isApprovedForAll(holder); if (msg.sender != holder) { require(msg.sender == operator || msg.sender == approved, "invalid request"); }

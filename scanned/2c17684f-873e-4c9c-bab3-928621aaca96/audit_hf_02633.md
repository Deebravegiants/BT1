# [C] Double-voting in BaseERC20Guild

## Summary
Severity: Critical
Contest weight: 0.2425
Dataset id: 14251
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract BaseERC20Guild enables users to cast votes on proposals using their voting powers. Voting power is acquired by locking tokens through the lockTokens() function, where the tokens will be locked until lockTime period passes. When a proposal is first submitted, the user can vote on this proposal by calling the setVote() function. Then, after casting their vote, the user can withdraw their tokens by calling withdrawTokens(). The token withdrawal does not revoke their proposal vote. Having their tokens back, the user can transfer the tokens to another account and vote again under the guise of a new user. This allows for double-voting. The scenario above is possible if the user locks tokens before a proposal is proposed, and therefore the lockTime expires before proposalTime passes. In this case, the system configuration where _lockTime >= _proposalTime does not prevent the user from withdrawing tokens before the proposalTime ends.

## Recommendation
Make sure this behaviour is intended. The testing team acknowledges that some implementation contracts have snapshot mechanism to mitigate this issue. However, other contracts such as DXDGuild, ERC20GuildWithERC1271, and EnforcedBinaryGuild do not have similar protection.

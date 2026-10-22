# [M] Non-whitelisted tokens cannot be added if the token limit is reached

## Summary
Severity: Medium
Contest weight: 0.1272
Dataset id: 19895
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Non-whitelisted tokens cannot be deposited to a bounty contract if too many whitelisted contracts were deposited.
The DepositManagerV1.fundBountyToken function allows depositing both whitelisted and non-whitelisted tokens by implementing the following check:
1. if a token is whitelisted, it can be deposited without restrictions;
2. if a token is not whitelisted, it cannot be deposited if openQTokenWhitelist.TOKEN_ADDRESS_LIMIT tokens have already been deposited.
However, while the token addresses limit requirement is only applied to non-whitelisted tokens, whitelisted tokens also increase the counter of token addresses: both non-whitelisted and whitelisted token addresses are added to the tokenAddresses set.
Bounty minters may not be able to deposit non-whitelisted tokens after they have deposited multiple whitelisted ones.

## Recommendation
Consider excluding whitelisted token addresses when checking the number of deposited tokens against the limit.

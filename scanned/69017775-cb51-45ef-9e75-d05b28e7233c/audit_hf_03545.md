# [M] GLPM-4 | User Forced To Deposit Both Tokens

## Summary
Severity: Medium
Contest weight: 0.1148
Dataset id: 19347
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In RewardRouter.sol for GMX V1, function unstakeAndRedeemGlp() requires that _glpAmount > 0: require(_glpAmount > 0, "RewardRouter: invalid _glpAmount"); In the GlpMigrator contract, if a user wants to only redeem for a the long token in a market, and leaves the GlpRedemption short with migrationItem.short.glpAmount = 0, the migration will fail due to the above revert. This is unexpected behavior as it forces users to not only populate the migrationItem.short.token to match the market's short token, but also set a miniscule amount of glpAmount to redeem for the short token to avoid migration failure. The same behavior applies if a user wants to solely redeem for the short token in a market, and leave the long token untouched.

## Recommendation
If the glpAmount for either the long or short token is 0, skip the call unstakeAndRedeemGlp() for that token.

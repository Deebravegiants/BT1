# [M] min/maxAnswer check is not done in for

## Summary
Severity: Medium
Contest weight: 0.1221
Dataset id: 2656
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Not validating for min/max answer on chainlink feeds can cause loss of funds for the credit issuer
When reading from Chainlink feeds validation is not done for min/max answers even though such oracles are used.
Eg: ETH/USD chainlink feed in optimism has min and max value set
Internal pre-conditions
External pre-conditions
Huge crash in price of tokens should occur
Attack Path
1. Price of token A drops below the minAnswer set on the feed (eg: 100 is the minAnswer and the token price goes to 1)
2. A statement is published with amount == 100
3. Attacker pays the statement balance by transferring 1 token A (incorrectly priced at 100 instead of 1) and the statement is settled
4. Loss for the credit issuer since they only receive 1 value compared to 100
Loss of funds for the credit issuer

## Recommendation
Check for the min/maxAnswer on the feeds and disallow payments using that token if the these thresholds are met

# [M] GLOBAL-2 | Block Re-org Attack

## Summary
Severity: Medium
Contest weight: 0.1249
Dataset id: 18508
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event of a block re-org a malicious trader may see that price has moved against them and
decide to get their order canceled rather than recorded.
Consider the following scenario:
Bob sees the keeper execute his MarketIncrease in block A
The block re-org occurs over a period of 1 minute
Bob sees the re-org is happening and sees that the execution of his order has since lost money
and gets his tx to cancel the order recorded in block B which will come before block A.
Bob can make his tx cancel his MarketIncrease by having it send the tokens necessary for the
MarketIncrease order elsewhere.
Bob’s order is canceled rather than executed since it did not net him any profit.
Notice that there are likely many ways to exploit the two-step execution process during a re-org.

## Recommendation
Beware of potential risks to the system during block re-orgs and communicate that risk with users.
Consider implementing a mechanism to freeze all orders that were executed during a block re-org.

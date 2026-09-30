# [M] M-08 | Missing Staleness Check For Chainlink Oracles

## Summary
Severity: Medium
Contest weight: 0.0839
Dataset id: 2265
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the price is fetched in functions like ﬂagPosition, the function will query Chainlink for the said price by calling the latestRoundData function. At this point, the price as well as the updatedAt are returned. The issue, however, is that the freshness of the price is not conﬁrmed, which can lead to stale prices being used to determine if a price is liquidatable or not. This can result in a position being wrongly liquidated using this function, and can lead to inaccurate proﬁt/losses when closing a position.

## Recommendation
Check and conﬁrm that the price is not stale when fetching Chainlink.

# [M] Invalid Redstone oracle payload size limit

## Summary
Severity: Medium
Contest weight: 0.1513
Dataset id: 23160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In api contract, it uses 224 bytes as maximum length for Redstone's oracle payload, but oracle price data and signatures of 3 signers exceeds 225 bytes thus reverting transactions.
In every external function of api contract, it uses 224 bytes as maximum size for Redstone oracle payload.
However, the RedstoneExtractor requires oracle data from at least 3 unique signers, as send token price information like token identifier, price, timestamp, etc and 65 bytes of signature data. Just with basic calculation, the oracle payload size exceeds 224 bytes.
Here's some proof of how Redstone oracle data is used:
• Check one of transactions from here that uses Redstone oracle.
• One of transaction is this one on Avalanche, which has 9571 bytes of data.
• Check this Blocksec Explorer, and it also shows the oracle data of 3 signers are passed.
As shown from the proof above, the payload size of Redstone data is huge, so setting 224 bytes as upperbound reverts transactions.
Protocol does not work because the payload array size limit is too small.

## Recommendation
The upperbound size of payload array should be increased to satisfy Redstone oracle payload size.

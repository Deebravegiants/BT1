# [M] M-02 | Sequencer Outage Risks

## Summary
Severity: Medium
Contest weight: 0.0521
Dataset id: 21430
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The sequencer uptime check is performed only in: Atomic Withdrawal, Normal Withdrawal and Liquidations. If sequencer is down, while it won't be possible to execute these functions, rest of the protocol will continue functioning if they don't have a priceFeed to check for reference price.

## Recommendation
Localize the sequencer checks to exactly where the Chainlink Aggregator Price is used.

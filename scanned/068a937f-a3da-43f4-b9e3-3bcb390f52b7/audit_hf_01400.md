# [M] M-5 Not reverting on the sequencer downtime

## Summary
Severity: Medium
Contest weight: 0.0697
Dataset id: 7175
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AggregateChainedOracle uses stored prices during the sequencer downtime:
• AggregateChainedOracle.sol#L145-L154
• Layer2UptimeOracle.sol#L31-L38
This is a risky approach, potentially leading to the use of irrelevant prices.
The approach demonstrated in Chainlink's documentation is different:
• https://docs.chain.link/data-feeds/l2-sequencer-feeds
The example, it reverts with SequencerDown() or GracePeriodNotOver().

## Recommendation
Consider reverting when the oracle reports sequencer downtime.

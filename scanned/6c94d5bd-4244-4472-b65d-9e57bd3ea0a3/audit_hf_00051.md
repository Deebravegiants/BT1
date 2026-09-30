# [M] GMOCL-2 | Use Of Deprecated latestAnswer Function

## Summary
Severity: Medium
Contest weight: 0.0752
Dataset id: 127
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _get function, the latestAnswer function is used to read the latest price from the Chainlink indexAggregator and shortAggregator. However the latestAnswer function is deprecated and should be replaced by a latestRoundData call with heartbeat validation as well as a sequencer uptime check for Arbitrum.

## Recommendation
Use the latestRoundData function to fetch the latest price from Chainlink and implement the necessary heartbeat and sequencer uptime validations. [Blockchain Oracles for Connected Smart Contracts | Chainlink Documentation](https://docs.chain.link/data-feeds/l2-sequencer-feeds) [Chainlink Data Feeds Documentation | Chainlink Documentation](https://docs.chain.link/data-feeds#check-the-timestamp-of-the-latest-answer)

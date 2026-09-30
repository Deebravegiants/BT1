# [M] M-28 | Missing Check For Sequencer Downtime

## Summary
Severity: Medium
Contest weight: 0.0804
Dataset id: 22199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Chainlink recommends that all Optimistic L2 oracles consult the Sequencer Uptime Feed to ensure that the sequencer is live before trusting the data returned by the oracle. See https://docs.chain.link/data-feeds#l2-sequencer-uptime-feeds If the Arbitrum sequencer goes down for example, oracle data will not be updated and could become stale. Attackers could take advantage of the stale prices and carry out attacks, such as borrowing more against their collateral's true value.

## Recommendation
Follow the code example of Chainlink: https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code

# [M] M-04 | Chainlink Price Lacks Price/Sequencer Validation

## Summary
Severity: Medium
Contest weight: 0.0910
Dataset id: 21958
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _check function in the KeeperProxy contract retrieves the Chainlink price; however, the price is fetched and used without performing any validation on the price or the sequencer status. Chainlink recommends following certain security practices, such as checking for stale or invalid prices. Additionally, when using Chainlink with L2 chains like Arbitrum, it is crucial to check whether the L2 Sequencer is down.

## Recommendation
Add validation checks to ensure the price retrieved by the _check function is not stale or invalid [Ref](https://medium.com/cyfrin/chainlink-oracle-defi-attacks-93b6cb6541bf). Also, implement sequencer feed checks to confirm the L2 Sequencer is operational before using the price data. Follow the Chainlink example for these checks as outlined in their [documentation](https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code).

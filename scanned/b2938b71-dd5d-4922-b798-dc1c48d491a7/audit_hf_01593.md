# [H] increaseNetworkTotal() allows big arbitrage opportunities by depositing before an increase transaction

## Summary
Severity: High
Contest weight: 0.1776
Dataset id: 8557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Increasing the network total is done via the increaseNetworkTotal() function call. Given that glAVAX allows instant withdrawals, it's very easy for MEV bots to steal rewards from legitimate users. They can front-run an increaseNetworkTotal() transaction, deposit AVAX, then the shares/wAVAX ratio increases and they withdraw, profiting without contributing to the network. Note that this does not happen in rebalance() because the ratio is maintained.

## Recommendation
Since the network is rebalanced every 24 hours, consider distributing the rewards over a 24h period. This way, bots can't steal yield from the network without having their wAVAX staked for the next rebalance call or contributing by letting other users withdraw. This could be achieved by setting a new state variable rewardsPerSecond which accrues to totalNetworkAVAX over a certain time period (24h would be enough because if bots deposited and wanted to claim the full amount they would have to wait 24h, which by then they AVAX could be used in the network). The bigger the interval, the smaller the MEV window.

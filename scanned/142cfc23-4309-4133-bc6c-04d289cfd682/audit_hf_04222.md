# [M] M-16 | Lacking Execution Incentive During Periods Of High Gas Fees

## Summary
Severity: Medium
Contest weight: 0.1256
Dataset id: 21116
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the test environment the maxKeeperFeeUsd is between $50 and $100, however this amount will be insufficient to incentivize the execution of orders and flagging of liquidatable positions during periods of high network usage and gas fees. The maxKeeperFeeUsd ought to be raised to sufficiently incentivize timely order execution and liquidation. Subsequently, some users may be unwilling to pay for extremely high execution costs during these times of high network usage. For these users it may be useful to have an order specific maximum keeper fee to limit the potential cost to their account’s margin.

## Recommendation
Consider raising the maxKeeperFeeUsd to a value that does not constrict the incentive for keepers to execute orders and flag positions for liquidation during periods of high gas fees. Based on the keeperSettlementGasUnits of 1.2 million and assuming an aggressive base fee of 40 gwei at a current price of $3,500 per ETH, the maxKeeperFeeUsd ought to be assigned to roughly $200+ to allow for appropriate incentives for order execution during periods of high network usage. Additionally consider implementing a maximum keeper fee value that is configurable on a per-order basis to allow users to set their tolerance for network fees.

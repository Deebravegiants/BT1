# [M] M-17 | Risk Free Trades With Rebalancer

## Summary
Severity: Medium
Contest weight: 0.2288
Dataset id: 153
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rebalancer is allowed to open positions at the current lastPrice immediately, without going through the initiation and validation process. This opens up the opportunity for risk free trades for the users who deposit into the rebalancer.
There there are several mechanisms in the Rebalancer to prevent the gameability of a risk free trade, but it is still possible to extract risk free value from the Rebalancer mechanism. The goal of an actor in this exploit is to get their deposit included in the rebalancer position to take advantage of an outdated lastPrice upon the triggering of the rebalancer.
A malicious actor can see when a large position or a large set of positions are close to being liquidated and initiate a deposit into the rebalancer. If the rebalancer is able to be triggered with a lastPrice that is less than the current market price within the [initiateRebalancerDeposit, initiateRebalancerDeposit + 24 seconds] window, then the user can immediately game the stale pricing by:
• Validating their rebalancer deposit
• triggering the rebalancer via a liquidation call
• Exiting the rebalancer with the initiateClosePosition function
If the correct conditions are not met within the timeframe, the actor can simply choose to not validate their deposit and wait until the cooldown period has ended to collect their funds. The actor can open consecutive initiate deposits with multiple addresses to ensure that they are able to take advantage of a rebalancer triggering in a given timeframe.

## Proof of Concept
https://gist.github.com/GuardianAudits/90ee8f9ea44a38a56ce33ca7c55bc555

## Recommendation
The extractable value from this grows with the size being liquidated and the imbalance created, however it is unlikely to occur with a great magnitude consistently. Therefore it may be fine to acknowledge this extractable value. Otherwise consider taking further measures to reduce the feasibility of this value extraction.
Such as introducing a fee upon validation or cancellation of a rebalancer deposit, or allowing other users to validate an arbitrary user's deposit so they do not have guaranteed optionality over the execution of their deposit.

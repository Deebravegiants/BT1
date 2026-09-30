# [C] C-01 | Rebalancer Position Closed Twice

## Summary
Severity: Critical
Contest weight: 0.1587
Dataset id: 133
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When initiating a close order for the rebalancer position with the initiateClosePosition function it is possible that the initiation of the close triggers the rebalancer itself. This results in many issues, including but not limited to: • Double counting the balance which is being closed • Removing the closed amount from the rebalancer's previous tick twice • Overwriting the state updates which were made in the Rebalancer.updatePosition function

## Proof of Concept
https://gist.github.com/GuardianAudits/5367834f1a429fe68bc5e5b00b8f8d59

## Recommendation
Revert the Rebalancer.initiateClosePosition function when a rebalancer is triggered by the _usdnProtocol.initiateClosePosition function call.

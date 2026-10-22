# [C] Re-entrancy Modiﬁer Misuse Causes Lost ETH

## Summary
Severity: Critical
Contest weight: 0.1730
Dataset id: 14459
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the reuse of the nonReentrant modiﬁer, ETH cannot be withdrawn from EigenLayer by the OperatorDelegator contract, causing any withdrawn ETH to be lost.
Both the receive() and completeQueuedWithdrawal() functions in OperatorDelegator have nonReentrant modiﬁers.
Since there is only a single nonReentrant guard in OpenZeppelin's ReentrancyGuardUpgradeable contract, functions with the nonReentrant modiﬁer cannot call one another. Hence, it is impossible for OperatorDelegator to receive ETH in completeQueuedWithdrawal() function, which would be the case if any natively restaked ETH was withdrawn from the EigenLayer beacon chain ETH strategy.

## Recommendation
Remove the nonReentrant modiﬁer from the receive() function in OperatorDelegator.

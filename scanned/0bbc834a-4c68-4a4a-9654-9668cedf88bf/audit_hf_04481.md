# [M] No way to cancel `l1 -< l2` messages

## Summary
Severity: Medium
Contest weight: 0.0733
Dataset id: 22028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no api to allow cancellation of `l1->l2` messages. In the event of an issue in the Kakarot contracts, this will result in the fee being permanently lost since the user has no ability to reclaim the funds.

As we can see there are only functions to either send the message from `l1 -> l2` or consume an `l2` message. There is no `cancelL1toL2Message` present.

## Recommendation
Introduce the following API to let users cancel their messages after waiting the time limit so that they can reclaim funds.

<https://docs.starknet.io/architecture-and-concepts/network-architecture/messaging-mechanism/#l2-l1_message_cancellation>

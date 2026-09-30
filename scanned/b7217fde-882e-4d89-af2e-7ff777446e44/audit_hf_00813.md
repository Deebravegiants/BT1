# [H] H-06 | _reorderQueue Does Not Work As Expected

## Summary
Severity: High
Contest weight: 0.1648
Dataset id: 2549
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SuperPool contract has deposit and withdrawal queues. Order of these queues are important since deposits and withdrawals are done based on the order, which is supposed to be arranged by the owner.
However, due to incorrect implementation of the _reorderQueue function, the owner can not change queue orders. This function takes a new order as an indexes array, and is supposed to rearrange the order based on indexes. But it only copies the previous order as is with the newQueue[i] = queue[i] line.

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-1/pull/5/files

## Recommendation
Use the inputted indexes array to determine new order. Change newQueue[i] = queue[i] to newQueue[i] = queue[indexes[i]].

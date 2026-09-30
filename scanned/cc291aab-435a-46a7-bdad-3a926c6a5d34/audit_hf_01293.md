# [H] Signature can be reused

## Summary
Severity: High
Contest weight: 0.1352
Dataset id: 6101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An authenticated address (say A) can join multiple times due to signature replay attack. The nonce used here also comes as an argument, hence can be reused. This has two issues: It blocks other authenticated addresses to participate. A can enter into the pot so many times that it becomes the majority in participants (up to numParticipants - 1 times). So with very high probability, it wins the pot effectively guaranteeing winning and taking other participants' contributions.

## Recommendation
Ensure that each authenticated address joins a round at most once.

# [M] M-10 | DoS In Dispute Process USDC Is Paused

## Summary
Severity: Medium
Contest weight: 0.0783
Dataset id: 2303
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The market’s dispute and escalation mechanisms rely on the ability to deposit bonds in USDC. If
USDC—being a pausable token—is paused, no new bonds can be deposited, effectively blocking any
new disputes or escalations.
An attacker can exploit this by proposing a resolution in their favor just before USDC becomes
paused; if the pause period extends past the challenge window, the outcome remains uncontested,
leading to unjust financial gains for the attacker.

## Recommendation
Extend dispute periods when USDC (or any payment token) is paused until transfers become
possible again.

# [H] H-02 | Malicious RateModel Attack

## Summary
Severity: High
Contest weight: 0.2026
Dataset id: 2545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• Anyone can create a BasePool with an arbitrary contract as RateModel
• Anyone can create a SuperPool
• The owner of a SuperPool can add a new BasePool to a SuperPool and reallocate all funds to it any time
These conditions allow the following attack:
• SuperPool owner creates a BasePool with a malicious RateModel and mints some shares
• SuperPool owner adds the BasePool to the queue of the SuperPool
• SuperPool owner reallocates all funds to the malicious BasePool
• The malicious actor calls accrue on the BasePool and the malicious RateModel returns that a lot of tokens in interest were accrued
• The malicious actor withdraws all funds in the BasePool with the few shares minted in the beginning and the users of the SuperPool lose everything

## Recommendation
Do not allow arbitrary addresses as RateModel.

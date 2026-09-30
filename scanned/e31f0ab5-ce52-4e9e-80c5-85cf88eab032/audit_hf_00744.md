# [M] M-08 | Lacking Incentives For The Escalator

## Summary
Severity: Medium
Contest weight: 0.0774
Dataset id: 2300
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, if the escalator is correct, the reward is sent to either the resolver or the disputor. This
assumes that the escalator is also the resolver or disputor.
However, considering that the escalator requires a larger bond, it’s possible that the resolver or
disputor does not have the required bond, and another party could step in and become the escalator.
This third party should be able to receive the reward independently for a correct escalation.

## Recommendation
Consider splitting the reward between the disputor/resolver and escalator when escalator is correct.

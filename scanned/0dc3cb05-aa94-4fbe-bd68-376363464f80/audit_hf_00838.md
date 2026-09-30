# [M] M-12 | Timelock Functionality Is Redundant

## Summary
Severity: Medium
Contest weight: 0.0781
Dataset id: 2574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some updates in the protocol require a 24-hour timelock period. These updates are requested initially and then accepted or rejected after the timelock period has elapsed. However, the requester, accepter, and rejecter are all the same person. A malicious owner could request an update days or weeks before it is actually needed and simply wait for the opportune moment to accept it, rendering the timelock feature ineffective.

## Recommendation
Consider implementing a deadline, such as 12 or 24 hours, for accepting a request after the timelock period has elapsed. Do not allow a pending request to be accepted after this deadline.

# [M] M-13 | Delegations Should Not Toggle Pools

## Summary
Severity: Medium
Contest weight: 0.1000
Dataset id: 2590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A pool is disconnected from a market and moved to 'outRange' after it has hit its maxValuePerShare usually through changes in market performance. However, it was observed that delegations may also move a pool in or out of range. In the case of a delegation (deposit), it was observed that the new delegator takes on the portion of the debt which was previous capped due to the pool being out of range. This appears to be unexpected for a delegator to immediately gain debt from the pool after delegating and in the worst case, the delegator could become instantly liquidatable from the debt.

## Recommendation
Consider re-examining the inRange/outRange mechanism to ensure that it can only move markets in or out based on market performance and not delegation as measured by creditCapacity.

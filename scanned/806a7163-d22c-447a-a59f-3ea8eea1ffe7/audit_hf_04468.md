# [M] M-10 | Keeper Actions Can Be Stalled By Deposits

## Summary
Severity: Medium
Contest weight: 0.1373
Dataset id: 21964
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol only allows one action to be processed at a time and depending on the action and circumstances each execution can take up to minutes to be finalized. As a result a malicious actor could intentionally create many small positions when the vault has no open position, and then when the vault has an open GMX position start triggering withdrawals from each account to DoS the protocol for an extended period. If each action takes 1 minute to process and the minimumDeposit amount is $10 then an attacker can DoS the protocol for one hour with $600 + gas. The attacker would recoup the majority of this upfront cost after they withdraw all shares. This cost may be profitable if the actor were a GM holder wanting to keep Gamma in a poor position for longer to reap PnL gains. Additionally a short-seller may be able to profit from such a DoS, spreading word of the trapped funds.

## Recommendation
Consider batching deposits and withdrawals to GMX to avoid DoS’s triggered by small individual accounts. Otherwise assign the minimum deposit value such that this attack is unprofitable.

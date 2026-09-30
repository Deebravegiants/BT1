# [M] Centralisation risk with liquidationResolver as it can steal 100% of locked funds

## Summary
Severity: Medium
Contest weight: 0.0870
Dataset id: 16600
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently the liquidationResolver has the power to steal 100% of locked funds in the following way:
1. Call freezeFunds for every user that has a locked balance
2. Wait some time until the liquidation delay has passed so the require statement in liquidateFunds succeeds
3. Call liquidateFunds and receive all of the users’ balances
This can happen if the liquidationResolver becomes malicious or is compromised.
Centralisation vulnerabilities usually require a malicious or a compromised account and are of Medium severity

## Recommendation
Reconsider if the freeze/liquidate funds is a mandatory mechanism for the protocol
Client response
Acknowledged

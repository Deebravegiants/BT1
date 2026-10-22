# [H] H-11 | Retrying Actions Causes DoS

## Summary
Severity: High
Contest weight: 0.1788
Dataset id: 21970
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an attempted order is canceled by GMX, the protocol chooses to handle this scenario by attempting to retry the previously attempted action. However, there are numerous reasons why the transaction may fail again. For instance, if the reserve ratio or open interest is out of balance for a market, if a market or action is disabled, or if GMX triggers Auto Deleveraging. A malicious user could even force this to occur by depositing, withdrawing, or swapping on GMX to attain one of these states. When this occurs Gamma’s flow will be stuck in its current state, and no other actions will be executable.

## Recommendation
Reset the transaction flow, and require the user or keeper to reattempt the action again. In the case of deposits, make sure that amount is refunded. Also consider adding additional admin privileged functions to terminate a flow, similar to cancelDeposit().

# [H] AIMUTI-2 | Withdrawal Keys Misused by Differing Subaccount in Liquidations

## Summary
Severity: High
Contest weight: 0.2810
Dataset id: 20544
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a liquidation is executed on an account from a vault with multiple accounts, a malicious actor
can pass the withdrawal key belonging to an account that is different from the one being liquidated
and block the vault.
Consider the scenario where a vault has accounts A and B:
By liquidating account A using account B’s key, account B’s withdrawal information is cleared. If
account B has a withdrawal that needs to be retried, the execution will fail as the stored withdrawal
information is empty.
Even if account B becomes liquidatable and uses account A’s key to perform the liquidation, that will
fail because DolomiteMargin would interpret that as a borrow increase in an unborrowable market.
This happens when account A’s withdrawal is for a larger amount that account B’s.
The vault remains frozen and all operations from any sub-accounts are blocked. Such a hijacked
liquidation can occur when both withdrawals have the same output token and are both retryable. The
withdrawal can be retryable from either an on-going liquidation or from a failed withdrawal of a
healthy position.

## Recommendation
In the _callFunction function, verify that the stored accountNumber matches the
_accountInfo.number but only if the call action was sent from a liquidation operation.
When sent from a liquidation operation, the _accountInfo.number variable holds the liquidatable
account but when sent from a normal unwrapping it is the ZAP account number.

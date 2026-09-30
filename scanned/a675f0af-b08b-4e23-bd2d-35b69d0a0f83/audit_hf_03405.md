# [H] ERTR-1 | UI Fee Manipulation

## Summary
Severity: High
Contest weight: 0.2731
Dataset id: 18513
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The uiFee can be manipulated during the order/deposit/withdrawal execution to determine whether
or not the action is executed and circumvent the validateRequestCancellation period.
Ultimately this allows malicious users to make a short-term risk-free trade as they can decide
whether or not their action should be executed successfully with prices from a few blocks ago.
For example, during a withdrawal, a malicious user can re-enter the system during the execution of
the first swap (WithdrawalUtils.sol: 388) into the ExchangeRouter.setUiFeeFactor function and
change the uiFeeFactor for the uiFeeReceiver of the withdrawal executed.
The change in uiFeeFactor can make the difference between the subsequent swap satisfying the
minOutputAmount — therefore deciding whether the withdrawal can go through.
Additionally, note that a similar effect can be achieved for any order/deposit/withdrawal by simply
front-running the execution tx and changing the uiFee.
Notice that malicious uiFeeReceivers can manipulate the uiFeeFactor after a user submits their
order/deposit/withdrawal. This way a uiFeeReceiver can promise a uiFee of .05%, but adjust it to be
much higher right before the actual execution.

## Recommendation
Do not allow the uiFeeFactor that is experienced in the execution to be changed after the
order/deposit/withdrawal is created/updated.

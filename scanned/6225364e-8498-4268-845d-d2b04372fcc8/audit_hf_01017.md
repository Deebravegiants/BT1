# [H] Rounding Issues

## Summary
Severity: High
Contest weight: 0.2029
Dataset id: 3670
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The application is accepting decimals in the Deposit and Withdraw function which is reflected immediately in the session balance (and rollup balance later on):

While the bets are always in rounded numbers, and the deposit, withdraw and finish seem to handle the decimals at the end of the game correctly, the reason this is classified as a High severity issue is that it might still present a potential issue of balance mishandling that the application is not expecting from the user input, considering it does not explicitly enforce the use of decimals and the backend might not be able to tackle the decimal rounding situations.
In the image: session balance 0.1 USDC remaining after playing.

In the image: rollup balance of 5.0889.

## Recommendation
Revise the input deposit/withdrawal amount that the user is able to introduce in both functions considering the ability to input decimals. If the application does not expect them, then the user should not be able to introduce these partial amounts.

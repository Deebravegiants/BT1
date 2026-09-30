# [C] C-02 | Frontrunning Loan Creations

## Summary
Severity: Critical
Contest weight: 0.2612
Dataset id: 20859
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each lending desk has a LoanConﬁg per nftCollection address, which contains the details about the minimum and maximum interest charged to the borrower. A malicious desk owner can front-run the initializeNewLoan call from the borrower, and change the loan conﬁguration with a large interest rate and a small duration, making the user pay more interest than they expected to pay when the new loan transaction was originated. Currently, there is no validation for maxInterest besides maxInterest>=minInterest. If the desk owner sets the interest the max allowed interest type(uint32).max = 4294967295 and conﬁgures the other Loan params to have constant interest, the borrower Loan interest will be set to minInterest chosen by desk owner. This means that the borrower will pay around 4900% per interest per hour and there is a minimum of 1 hour wait to repay the loan. In summary, a malicious lender can set a small interest rate to honeypot borrowers, update the loan conﬁguration before their transaction is initialized, and lock the borrower in at the max interest rate for at least an hour which they must pay.

## Recommendation
Add an extra parameter to the initializedNewLoan function, where the borrower can set a maxInterestAllowed, which will act as a limit on what they are willing to pay.

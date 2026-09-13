# [M] 6.2 Full Balance Is Pushed on Reconciliation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

To handle direct token transfers to the loan contract as repayments (and to handle arbitrary tokens
received), Avantgarde Finance introduces a reconciliation functionality for arbitrary loans, which allows
moving arbitrary tokens received (e.g., insurance payments) to be moved to the vault. Furthermore, it
considers all surplus balance (compared to the borrowable amount) of the loan token as a repayment.
However, it always moves the full loan token balance to the vault. While this makes sense when closing
the vault, it may break the loan's logic when action reconcile is executed (e.g., borrowable amount > 0 but
borrows are impossible).

Code corrected:

Reconciliation for the Reconcile action and reconciliation for the Close action are now performed
differently. A boolean _close argument was added to the __reconcile function to make this
distinction.

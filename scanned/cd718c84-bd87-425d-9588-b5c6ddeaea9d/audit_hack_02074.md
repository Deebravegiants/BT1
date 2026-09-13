# [M] 6.3 No Sanity Check on Revenue Share

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

Partners can earn a share of the administrator fee. The percentage can be set with
PermittedPartners.setPartnerRevenueShare(). However, this method does not check whether
the share exceeds 100%.

Assume a loan starts where that is the case. Then, this percentage would be stored in the loan extras of
a loan which cannot be renegotiated nor modified in any way for the loan. Paying back the loan will
ultimately revert since an underflow would occur when computing the fee left for the administrator.
Hence, the borrower cannot retrieve his collateral back and liquidation is the only possibility to exit the
loan.

Code corrected:

100% cannot be exceeded anymore.

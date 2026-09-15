# [H] CVE-2019-16753

## Summary
Severity: High
Advisory: CVE-2019-16753
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-16753
Type: osv

## Details
An issue was discovered in Decentralized Anonymous Payment System (DAPS) through 2019-08-26. The content to be signed is composed of a representation of strings, rather than being composed of their binary representations. This is a weak signature scheme design that would allow the reuse of signatures in some cases (or even the reuse of signatures, intended for one type of message, for another type). This also affects Private Instant Verified Transactions (PIVX) through 3.4.0.

## References
- https://officialdapscoin.com/wp-content/uploads/2019/09/DAPS-Coin-Final-Security-Audit-Red4Sec-2019.pdf

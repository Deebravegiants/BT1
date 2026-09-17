# [M] CVE-2021-29023

## Summary
Severity: Medium
Advisory: CVE-2021-29023
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2021-29023
Type: osv

## Details
InvoicePlane 1.5.11 doesn't have any rate-limiting for password reset and the reset token is generated using a weak mechanism that is predictable.

## References
- https://seran.github.io/research/2021/03/16/weak-password-recovery-mechanism-in-invoiceplane.html
- https://notnnor.github.io/research/2021/03/16/weak-password-recovery-mechanism-in-invoiceplane.html
- https://github.com/InvoicePlane/InvoicePlane/pull/767

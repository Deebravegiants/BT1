# [H] CVE-2021-29024

## Summary
Severity: High
Advisory: CVE-2021-29024
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2021-29024
Type: osv

## Details
In InvoicePlane 1.5.11 a misconfigured web server allows unauthenticated directory listing and file download. Allowing an attacker to directory traversal and download files suppose to be private without authentication.

## References
- https://seran.github.io/research/2021/03/17/files-or-directories-accessible-to-external-parties-in-invoiceplane.html
- https://notnnor.github.io/research/2021/03/17/files-or-directories-accessible-to-external-parties-in-invoiceplane.html
- https://github.com/InvoicePlane/InvoicePlane/pull/754

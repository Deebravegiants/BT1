# [C] CVE-2021-3694

## Summary
Severity: Critical
Advisory: CVE-2021-3694
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3694
Type: osv

## Details
LedgerSMB does not sufficiently HTML-encode error messages sent to the browser. By sending a specially crafted URL to an authenticated user, this flaw can be abused for remote code execution and information disclosure.

## References
- https://huntr.dev/bounties/ef7f4cf7-3a81-4516-b261-f5b6ac21430c
- https://ledgersmb.org/cve-2021-3694-cross-site-scripting
- https://www.debian.org/security/2021/dsa-4962
- https://github.com/ledgersmb/ledgersmb/commit/98fa476d46a4a7e5e9492ed69b4fa190be5547fc

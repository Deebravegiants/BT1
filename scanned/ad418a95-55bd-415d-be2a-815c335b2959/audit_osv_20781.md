# [C] CVE-2021-3693

## Summary
Severity: Critical
Advisory: CVE-2021-3693
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3693
Type: osv

## Details
LedgerSMB does not check the origin of HTML fragments merged into the browser's DOM. By sending a specially crafted URL to an authenticated user, this flaw can be abused for remote code execution and information disclosure.

## References
- https://huntr.dev/bounties/daf1384d-648a-43fd-9b35-5c37d8ead667
- https://www.debian.org/security/2021/dsa-4962
- https://ledgersmb.org/cve-2021-3693-cross-site-scripting

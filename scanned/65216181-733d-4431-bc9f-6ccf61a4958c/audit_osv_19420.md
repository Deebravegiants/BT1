# [M] CVE-2021-21260

## Summary
Severity: Medium
Advisory: CVE-2021-21260
Aliases: GHSA-rm79-5596-r7q4
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-01-22
Source: https://osv.dev/vulnerability/CVE-2021-21260
Type: osv

## Details
Online Invoicing System (OIS) is open source software which is a lean invoicing system for small businesses, consultants and freelancers created using AppGini. In OIS version 4.0 there is a stored XSS which can enables an attacker takeover of the admin account through a payload that extracts a csrf token and sends a request to change password. It has been found that Item description is reflected without sanitization in app/items_view.php which enables the malicious scenario.

## References
- https://github.com/bigprof-software/online-invoicing-system/releases/tag/4.2
- https://github.com/bigprof-software/online-invoicing-system/security/advisories/GHSA-rm79-5596-r7q4

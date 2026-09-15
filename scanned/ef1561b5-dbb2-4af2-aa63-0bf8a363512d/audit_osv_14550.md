# [H] CVE-2019-1010246

## Summary
Severity: High
Advisory: CVE-2019-1010246
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-1010246
Type: osv

## Details
MailCleaner before c888fbb6aaa7c5f8400f637bcf1cbb844de46cd9 is affected by: Unauthenticated MySQL database password information disclosure. The impact is: MySQL database content disclosure (e.g. username, password). The component is: The API call in the function allowAction() in NewslettersController.php. The attack vector is: HTTP Get request. The fixed version is: c888fbb6aaa7c5f8400f637bcf1cbb844de46cd9.

## References
- https://github.com/MailCleaner/MailCleaner/commit/c888fbb6aaa7c5f8400f637bcf1cbb844de46cd9

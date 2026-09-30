# [H] CVE-2020-17366

## Summary
Severity: High
Advisory: CVE-2020-17366
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-08-05
Source: https://osv.dev/vulnerability/CVE-2020-17366
Type: osv

## Details
An issue was discovered in NLnet Labs Routinator 0.1.0 through 0.7.1. It allows remote attackers to bypass intended access restrictions or to cause a denial of service on dependent routing systems by strategically withholding RPKI Route Origin Authorisation ".roa" files or X509 Certificate Revocation List files from the RPKI relying party's view.

## References
- https://github.com/NLnetLabs/routinator/releases/tag/v0.8.0
- https://github.com/NLnetLabs/routinator/issues/319

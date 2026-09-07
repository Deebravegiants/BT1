# [M] Dutchoders transfer.sh contains an XSS vulnerability via malicious file upload

## Summary
Severity: Medium
Advisory: GHSA-pwq7-f7f9-cm2j
CVE: CVE-2022-40931
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-pwq7-f7f9-cm2j
Type: github-advisory

## Affected
- Go: `github.com/dutchcoders/transfer.sh` — affected >=0

## Details
dutchcoders Transfer.sh versions 1.4.0 and prior are vulnerable to Cross Site Scripting (XSS) via a malicious document uploaded in transfer.sh.  There is a fix commit merged into [main](https://github.com/dutchcoders/transfer.sh/commit/31ad4e01e158497519f8680c187e1ceb8594c59d) for this issue, but an updated version has not yet been released.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40931
- https://github.com/dutchcoders/transfer.sh/issues/500
- https://github.com/dutchcoders/transfer.sh/pull/501
- https://github.com/dutchcoders/transfer.sh

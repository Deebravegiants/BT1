# [C] CVE-2020-36561

## Summary
Severity: Critical
Advisory: CVE-2020-36561
Aliases: GHSA-f5c5-hmw9-v8hx, GO-2020-0035
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2020-36561
Type: osv

## Details
Due to improper path sanitization, archives containing relative file paths can cause files to be written (or overwritten) outside of the target directory.

## References
- https://pkg.go.dev/vuln/GO-2020-0035
- https://snyk.io/research/zip-slip-vulnerability
- https://github.com/yi-ge/unzip/commit/2adbaa4891b9690853ef10216189189f5ad7dc73
- https://github.com/yi-ge/unzip/pull/1

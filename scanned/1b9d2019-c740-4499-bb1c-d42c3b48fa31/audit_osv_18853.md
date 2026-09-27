# [C] CVE-2020-36560

## Summary
Severity: Critical
Advisory: CVE-2020-36560
Aliases: GHSA-rmj9-q58g-9qgg, GO-2020-0034
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2020-36560
Type: osv

## Details
Due to improper path sanitization, archives containing relative file paths can cause files to be written (or overwritten) outside of the target directory.

## References
- https://pkg.go.dev/vuln/GO-2020-0034
- https://snyk.io/research/zip-slip-vulnerability
- https://github.com/artdarek/go-unzip/commit/4975cbe0a719dc50b12da8585f1f207c82f7dfe0
- https://github.com/artdarek/go-unzip/pull/2

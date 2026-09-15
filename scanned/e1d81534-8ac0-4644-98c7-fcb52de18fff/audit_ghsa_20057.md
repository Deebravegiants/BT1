# [C] Cloud Foundry Archiver vulnerable to path traversal

## Summary
Severity: Critical
Advisory: GHSA-32qh-8vg6-9g43
CVE: CVE-2018-25046
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-32qh-8vg6-9g43
Type: github-advisory

## Affected
- Go: `github.com/cloudfoundry/archiver` — affected >=0 <0.0.0-20180523222229-09b5706aa936
- Go: `code.cloudfoundry.org/archiver` — affected >=0 <0.0.0-20180523222229-09b5706aa936

## Details
Due to improper path santization, archives containing relative file paths can cause files to be written (or overwritten) outside of the target directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25046
- https://github.com/cloudfoundry/archiver/commit/09b5706aa9367972c09144a450bb4523049ee840
- https://github.com/cloudfoundry/archiver
- https://pkg.go.dev/vuln/GO-2020-0025
- https://snyk.io/research/zip-slip-vulnerability

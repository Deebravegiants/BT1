# [H] github.com/sassoftware/go-rpmutils Arbitrary File Write via Archive Extraction (Zip Slip)

## Summary
Severity: High
Advisory: GHSA-9423-6c93-gpp8
CVE: CVE-2020-7667
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-9423-6c93-gpp8
Type: github-advisory

## Affected
- Go: `github.com/sassoftware/go-rpmutils` — affected >=0 <0.1.0

## Details
The CPIO extraction functionality doesn't sanitize the paths of the archived files for leading and non-leading `..` which leads in file extraction outside of the current directory. Note, the fixing commit was applied to all affected versions which were re-released.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7667
- https://github.com/sassoftware/go-rpmutils/commit/a64058cf21b8aada501bba923c9aab66fb6febf0
- https://github.com/sassoftware/go-rpmutils
- https://pkg.go.dev/vuln/GO-2020-0042
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMSASSOFTWAREGORPMUTILSCPIO-570427

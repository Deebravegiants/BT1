# [H] github.com/u-root/u-root/pkg/tarutil Arbitrary File Write via Archive Extraction (Zip Slip)

## Summary
Severity: High
Advisory: GHSA-75qf-wgfj-v652
CVE: CVE-2020-7669
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-75qf-wgfj-v652
Type: github-advisory

## Affected
- Go: `github.com/u-root/u-root` — affected >=0 <0.9.0

## Details
This affects all versions up to and including version 0.7.0 of package github.com/u-root/u-root/pkg/tarutil. It is vulnerable to both leading and non-leading relative path traversal attacks in tar file extraction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7669
- https://github.com/u-root/u-root/issues/2449
- https://github.com/u-root/u-root/pull/1817
- https://github.com/u-root/u-root/pull/2344
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMUROOTUROOTPKGTARUTIL-570428

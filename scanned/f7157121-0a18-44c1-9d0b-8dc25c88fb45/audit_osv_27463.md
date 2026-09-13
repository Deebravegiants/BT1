# [H] Iodine Static File Server Path Traversal Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-22050
Aliases: GHSA-85rf-xh54-whp3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-04
Source: https://osv.dev/vulnerability/CVE-2024-22050
Type: osv

## Details
Path traversal in the static file service in Iodine less than 0.7.33 allows an unauthenticated, remote attacker to read files outside the public folder via malicious URLs.

## References
- https://rubygems.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22050.json
- https://github.com/advisories/GHSA-85rf-xh54-whp3
- https://github.com/boazsegev/iodine/security/advisories/GHSA-85rf-xh54-whp3
- https://nvd.nist.gov/vuln/detail/CVE-2024-22050
- https://vulncheck.com/advisories/vc-advisory-GHSA-85rf-xh54-whp3
- https://github.com/boazsegev/iodine/commit/5558233fb7defda706b4f9c87c17759705949889

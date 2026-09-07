# [H] Path traversal in claircore

## Summary
Severity: High
Advisory: GHSA-mq47-6wwv-v79w
CVE: CVE-2021-3762
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-mq47-6wwv-v79w
Type: github-advisory

## Affected
- Go: `github.com/quay/claircore` — affected >=0 <0.4.8
- Go: `github.com/quay/claircore` — affected >=1.0.0 <1.1.0
- Go: `github.com/quay/claircore` — affected >=0.5.0 <0.5.5

## Details
A directory traversal vulnerability was found in the ClairCore engine of Clair. An attacker can exploit this by supplying a crafted container image which, when scanned by Clair, allows for arbitrary file write on the filesystem, potentially allowing for remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3762
- https://github.com/quay/clair/pull/1379
- https://github.com/quay/clair/pull/1380
- https://github.com/quay/claircore/pull/478
- https://github.com/quay/claircore/commit/691f2023a1720a0579e688b69a2f4bfe1f4b7821
- https://github.com/quay/claircore/commit/dff671c665141f126c072de8a744855d4916c9c7
- https://github.com/quay/claircore/commit/ed5f52aec1c82746725e9cc23e98316eab8be25a
- https://bugzilla.redhat.com/show_bug.cgi?id=2000795
- https://github.com/quay/claircore
- https://github.com/quay/claircore/commits/v0.4.8
- https://github.com/quay/claircore/commits/v0.5.5
- https://github.com/quay/claircore/commits/v1.1.0
- https://pkg.go.dev/vuln/GO-2022-0346
- https://vulmon.com/exploitdetails?qidtp=maillist_oss_security&qid=d19fce9ede06e13dfb5630ece7f14f83

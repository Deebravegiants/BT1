# [H] Information Exposure in Heketi

## Summary
Severity: High
Advisory: GHSA-q9vw-wr57-xjv3
CVE: CVE-2017-15104
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-q9vw-wr57-xjv3
Type: github-advisory

## Affected
- Go: `github.com/heketi/heketi` — affected >=0 <5.0.1

## Details
An access flaw was found in Heketi 5, where the heketi.json configuration file was world readable. An attacker having local access to the Heketi server could read plain-text passwords from the heketi.json file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15104
- https://github.com/heketi/heketi/commit/787bae461b23003a4daa4d1d639016a754cf6b00
- https://access.redhat.com/errata/RHSA-2017:3481
- https://access.redhat.com/security/cve/CVE-2017-15104
- https://bugzilla.redhat.com/show_bug.cgi?id=1510149
- https://github.com/heketi/heketi/releases/tag/v5.0.1

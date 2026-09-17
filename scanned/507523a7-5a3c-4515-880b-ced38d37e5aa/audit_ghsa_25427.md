# [M] Heketi logs sensitive information

## Summary
Severity: Medium
Advisory: GHSA-rm7c-x6gj-2mr8
CVE: CVE-2020-10763
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rm7c-x6gj-2mr8
Type: github-advisory

## Affected
- Go: `github.com/heketi/heketi` — affected >=0 <10.1.0

## Details
An information-disclosure flaw was found in the way Heketi before 10.1.0 logs sensitive information. This flaw allows an attacker with local access to the Heketi server to read potentially sensitive information such as gluster-block passwords.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10763
- https://github.com/heketi/heketi/commit/be1583833924e62d2581824a0addcba0aed33c99
- https://bugzilla.redhat.com/show_bug.cgi?id=1845387
- https://github.com/heketi/heketi/releases/tag/v10.1.0

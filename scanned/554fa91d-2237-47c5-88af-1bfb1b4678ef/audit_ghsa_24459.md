# [M] Gitea Arbitrary File Delete Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j99q-rwp6-498g
CVE: CVE-2019-1000002
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j99q-rwp6-498g
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.6.3

## Details
Gitea version 1.6.2 and earlier contains a Incorrect Access Control vulnerability in Delete/Edit file functionallity that can result in the attacker deleting files outside the repository he/she has access to. This attack appears to be exploitable via the attacker must get write access to "any" repository including self-created ones. This vulnerability appears to have been fixed in 1.6.3, 1.7.0-rc2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000002
- https://github.com/go-gitea/gitea/pull/5631
- https://github.com/go-gitea/gitea

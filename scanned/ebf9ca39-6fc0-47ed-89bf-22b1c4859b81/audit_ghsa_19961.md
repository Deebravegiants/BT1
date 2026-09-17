# [M] go-saml's XML Digital Signatures use SHA-1

## Summary
Severity: Medium
Advisory: GHSA-5rhg-xhgr-5hfj
CVE: CVE-2020-36563
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-5rhg-xhgr-5hfj
Type: github-advisory

## Affected
- Go: `github.com/RobotsAndPencils/go-saml` — affected >=0

## Details
XML Digital Signatures generated and validated using this package use SHA-1, which may allow an attacker to craft inputs which cause hash collisions depending on their control over the input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36563
- https://github.com/RobotsAndPencils/go-saml/pull/38
- https://github.com/RobotsAndPencils/go-saml/commit/4a1b1f5752a029e171965e0510a425d0fdd1eced
- https://github.com/RobotsAndPencils/go-saml
- https://pkg.go.dev/vuln/GO-2020-0047

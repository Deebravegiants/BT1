# [M] gopkg.in/macaron.v1 Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-733f-44f3-3frw
CVE: CVE-2020-12666
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-733f-44f3-3frw
Type: github-advisory

## Affected
- Go: `gopkg.in/macaron.v1` — affected >=0 <1.3.7

## Details
macaron before 1.3.7 has an open redirect in the static handler. Due to improper request santization, a specifically crafted URL can cause the static file handler to redirect to an attacker chosen URL, allowing for open redirect attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12666
- https://github.com/go-macaron/macaron/issues/198
- https://github.com/go-macaron/macaron/issues/198#issuecomment-622885959
- https://github.com/go-macaron/macaron/pull/199
- https://github.com/go-macaron/macaron/pull/199/commits/6bd9385542f7133467ab7d09a5f28f7d5dc52af7
- https://github.com/go-macaron/macaron/commit/addc7461c3a90a040e79aa75bfd245107a210245
- https://github.com/go-macaron/macaron
- https://github.com/go-macaron/macaron/releases/tag/v1.3.7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3QEUOHRC4EN4WZ66EVFML2UCV7ZQ63XZ
- https://pkg.go.dev/vuln/GO-2020-0039

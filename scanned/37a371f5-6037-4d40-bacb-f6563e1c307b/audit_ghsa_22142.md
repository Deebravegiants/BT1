# [H] Rancher Access Control Vulnerability

## Summary
Severity: High
Advisory: GHSA-w3x4-9854-95x8
CVE: CVE-2017-7297
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w3x4-9854-95x8
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=1.5.0 <1.5.3
- Go: `github.com/rancher/rancher` — affected >=1.4.0 <1.4.3
- Go: `github.com/rancher/rancher` — affected >=1.3.0 <1.3.5
- Go: `github.com/rancher/rancher` — affected >=1.2.0 <1.2.4

## Details
Rancher Labs rancher server 1.2.0+ is vulnerable to authenticated users disabling access control via an API call. This is fixed in versions rancher/server:v1.2.4, rancher/server:v1.3.5, rancher/server:v1.4.3, and rancher/server:v1.5.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7297
- https://github.com/rancher/rancher/issues/8296
- https://github.com/rancher/rancher
- https://web.archive.org/web/20200227181556/http://www.securityfocus.com/bid/97180

# [C] Apache Traffic Control Traffic Ops Vulnerable to LDAP Injection

## Summary
Severity: Critical
Advisory: GHSA-mg2c-rc36-p594
CVE: CVE-2021-43350
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mg2c-rc36-p594
Type: github-advisory

## Affected
- Go: `github.com/apache/trafficcontrol` — affected >=6.0.0 <6.0.1
- Go: `github.com/apache/trafficcontrol` — affected >=5.1.0 <5.1.4

## Details
An unauthenticated Apache Traffic Control Traffic Ops user can send a request with a specially-crafted username to the POST `/login` endpoint of any API version to inject unsanitized content into the LDAP filter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43350
- https://github.com/apache/trafficcontrol
- https://pkg.go.dev/vuln/GO-2024-2776
- https://trafficcontrol.apache.org/security
- http://www.openwall.com/lists/oss-security/2021/11/11/3
- http://www.openwall.com/lists/oss-security/2021/11/11/4
- http://www.openwall.com/lists/oss-security/2021/11/17/1

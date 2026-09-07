# [C] Grafana Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-rgjg-66cx-5x9m
CVE: CVE-2018-15727
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-rgjg-66cx-5x9m
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <4.6.4
- Go: `github.com/grafana/grafana` — affected >=5.0.0 <5.2.3

## Details
Grafana before 4.6.4 and 5.x before 5.2.3 allows authentication bypass because an attacker can generate a valid "remember me" cookie knowing only a username of an LDAP or OAuth user.

### Specific Go Packages Affected
github.com/grafana/grafana/pkg/api

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15727
- https://github.com/grafana/grafana/commit/7baecf0d0deae0d865e45cf03e082bc0db3f28c3
- https://github.com/grafana/grafana/commit/df83bf10a225811927644bdf6265fa80bdea9137
- https://access.redhat.com/errata/RHSA-2018:3829
- https://access.redhat.com/errata/RHSA-2019:0019
- https://grafana.com/blog/2018/08/29/grafana-5.2.3-and-4.6.4-released-with-important-security-fix
- https://www.securityfocus.com/bid/105184

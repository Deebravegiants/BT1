# [M] Denial of service in Grafana

## Summary
Severity: Medium
Advisory: GHSA-h5rh-w6vm-9ghc
CVE: CVE-2021-27358
CWE: CWE-306, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H/E:U/RL:O/RC:R (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-h5rh-w6vm-9ghc
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=6.7.3 <7.4.2

## Details
The snapshot feature in Grafana before 7.4.2 can allow an unauthenticated remote attackers to trigger a Denial of Service via a remote API call if a commonly used configuration is set.
### Specific Go Packages Affected
github.com/grafana/grafana/pkg/middleware

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27358
- https://github.com/grafana/grafana/pull/31263
- https://github.com/grafana/grafana/blob/master/CHANGELOG.md
- https://github.com/grafana/grafana/blob/master/CHANGELOG.md#742-2021-02-17
- https://grafana.com/docs/grafana/latest/release-notes/release-notes-7-4-2
- https://security.netapp.com/advisory/ntap-20210513-0007

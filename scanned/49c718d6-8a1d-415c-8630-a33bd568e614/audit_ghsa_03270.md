# [C] Improper Authentication in InfluxDB

## Summary
Severity: Critical
Advisory: GHSA-2rmp-fw5r-j5qv
CVE: CVE-2019-20933
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-2rmp-fw5r-j5qv
Type: github-advisory

## Affected
- Go: `github.com/influxdata/influxdb` — affected >=0 <1.7.6

## Details
InfluxDB before 1.7.6 has an authentication bypass vulnerability in the authenticate function in `services/httpd/handler.go` because a JWT token may have an empty SharedSecret (aka shared secret).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20933
- https://github.com/influxdata/influxdb/issues/12927
- https://github.com/influxdata/influxdb/commit/761b557315ff9c1642cf3b0e5797cd3d983a24c0
- https://github.com/influxdata/influxdb/compare/v1.7.5...v1.7.6
- https://github.com/ticarpi/jwt_tool/blob/a6ca3e0524a204b5add070bc6874cb4e7e5a9864/jwt_tool.py#L1368
- https://lists.debian.org/debian-lts-announce/2020/12/msg00030.html
- https://pkg.go.dev/github.com/influxdata/influxdb/services/httpd
- https://www.debian.org/security/2021/dsa-4823

# [C] Access control bypass in beego

## Summary
Severity: Critical
Advisory: GHSA-qx32-f6g6-fcfr
CVE: CVE-2022-31259
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-22
Source: https://github.com/advisories/GHSA-qx32-f6g6-fcfr
Type: github-advisory

## Affected
- Go: `github.com/beego/beego/v2` — affected >=0 <2.0.3
- Go: `github.com/beego/beego` — affected >=0 <1.12.9

## Details
The route lookup process in beego prior to 1.12.9 and 2.x prior to 2.0.3 allows attackers to bypass access control. When a /`p1`/`p2`/`:name` route is configured, attackers can access it by appending .xml in various places (e.g., p1.xml instead of p1).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31259
- https://github.com/beego/beego/issues/4946
- https://github.com/beego/beego/pull/4954
- https://github.com/beego/beego/pull/4958
- https://github.com/beego/beego/commit/228576173a236c81a2122923fcf8099ad294e009
- https://github.com/beego/beego/commit/64cf44d725c8cc35d782327d333df9cbeb1bf2dd
- https://github.com/advisories/GHSA-qx32-f6g6-fcfr
- https://github.com/beego/beego
- https://github.com/beego/beego/tree/v2.0.2
- https://pkg.go.dev/vuln/GO-2022-0463

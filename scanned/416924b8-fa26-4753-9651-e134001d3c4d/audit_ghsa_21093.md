# [C] Path Traversal in Beego

## Summary
Severity: Critical
Advisory: GHSA-95f9-94vc-665h
CVE: CVE-2022-31836
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-06
Source: https://github.com/advisories/GHSA-95f9-94vc-665h
Type: github-advisory

## Affected
- Go: `github.com/beego/beego` — affected >=0 <1.12.11
- Go: `github.com/beego/beego/v2` — affected >=2.0.0 <2.0.4

## Details
The `leafInfo.match()` function in Beego v2.0.3 and below uses `path.join()` to deal with wildcardvalues which can lead to cross directory risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31836
- https://github.com/beego/beego/issues/4961
- https://github.com/beego/beego/pull/5025
- https://github.com/beego/beego/pull/5025/commits/ea5ae58d40589d249cf577a053e490509de2bf57
- https://github.com/advisories/GHSA-95f9-94vc-665h
- https://github.com/beego/beego
- https://pkg.go.dev/vuln/GO-2022-0569

# [M] dhowden tag panic due to out-of-bounds read

## Summary
Severity: Medium
Advisory: GHSA-27mh-3343-6hg5
CVE: CVE-2020-29244
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-27mh-3343-6hg5
Type: github-advisory

## Affected
- Go: `github.com/dhowden/tag` — affected >=0 <0.0.0-20201120070457-d52dcb253c63

## Details
Due to improper bounds checking, a number of methods in dhowden tag before 0.0.0-20201120070457-d52dcb253c63 can trigger a panic due to attempted out-of-bounds reads. If the package is used to parse user supplied input, this may be used as a vector for a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29244
- https://github.com/dhowden/tag/issues/79
- https://github.com/dhowden/tag/commit/4b595ed4fac79f467594aa92f8953f90f817116e
- https://github.com/dhowden/tag/commit/6b18201aa5c5535511802ddfb4e4117686b4866d
- https://github.com/dhowden/tag/commit/a92213460e4838490ce3066ef11dc823cdc1740e
- https://github.com/dhowden/tag/commit/d52dcb253c63a153632bfee5f269dd411dcd8e96
- https://github.com/dhowden/tag
- https://pkg.go.dev/vuln/GO-2021-0097

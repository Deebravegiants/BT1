# [M] Denial of Service in dhowden/tag

## Summary
Severity: Medium
Advisory: GHSA-9xm8-8qvc-vw3p
CVE: CVE-2020-29242
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L/E:P/RL:O/RC:C (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-9xm8-8qvc-vw3p
Type: github-advisory

## Affected
- Go: `github.com/dhowden/tag` — affected >=0 <0.0.0-20201120070457-d52dcb253c63

## Details
dhowden tag before 0.0.0-20201120070457-d52dcb253c63 allows `panic: runtime error: index out of range` via readPICFrame.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29242
- https://github.com/dhowden/tag/issues/77
- https://github.com/dhowden/tag/issues/78
- https://github.com/dhowden/tag/issues/79
- https://github.com/dhowden/tag/issues/80
- https://github.com/dhowden/tag/commit/4b595ed4fac79f467594aa92f8953f90f817116e
- https://github.com/dhowden/tag/commit/6b18201aa5c5535511802ddfb4e4117686b4866d
- https://github.com/dhowden/tag/commit/a92213460e4838490ce3066ef11dc823cdc1740e
- https://github.com/dhowden/tag/commit/d52dcb253c63a153632bfee5f269dd411dcd8e96
- https://github.com/dhowden/tag
- https://pkg.go.dev/vuln/GO-2021-0097

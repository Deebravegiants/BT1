# [H] Hybrid Group Gobot Improper Certificate Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-vfxc-r2gx-v2vq
CVE: CVE-2019-12496
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vfxc-r2gx-v2vq
Type: github-advisory

## Affected
- Go: `github.com/hybridgroup/gobot` — affected >=0 <1.12.1-0.20190521122906-c1aa4f867846

## Details
An issue was discovered in Hybrid Group Gobot before 1.13.0. The mqtt subsystem skips verification of root CA certificates by default.

### Specific Go Packages Affected
github.com/hybridgroup/gobot/platforms/mqtt

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12496
- https://github.com/hybridgroup/gobot/commit/c1aa4f867846da4669ecf3bc3318bd96b7ee6f3f
- https://github.com/hybridgroup/gobot
- https://github.com/hybridgroup/gobot/compare/ed53198...7f973df
- https://github.com/hybridgroup/gobot/releases/tag/v1.13.0
- https://pkg.go.dev/vuln/GO-2021-0083

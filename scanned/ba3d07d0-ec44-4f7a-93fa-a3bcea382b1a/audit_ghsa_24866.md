# [H] HashiCorp go-getter unsafe downloads could lead to arbitrary host access

## Summary
Severity: High
Advisory: GHSA-cjr4-fv6c-f3mv
CVE: CVE-2022-30322
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-05-26
Source: https://github.com/advisories/GHSA-cjr4-fv6c-f3mv
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-getter` — affected >=0 <1.6.1
- Go: `github.com/hashicorp/go-getter` — affected >=2.0.0 <2.1.0
- Go: `github.com/hashicorp/go-getter/v2` — affected >=0 <2.1.0
- Go: `github.com/hashicorp/go-getter/s3/v2` — affected >=0 <2.1.0
- Go: `github.com/hashicorp/go-getter/gcs/v2` — affected >=0 <2.1.0

## Details
HashiCorp go-getter through 2.0.2 does not safely perform downloads. Arbitrary host access was possible via go-getter path traversal, symlink processing, and command injection flaws.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30322
- https://github.com/hashicorp/go-getter/pull/359
- https://github.com/hashicorp/go-getter/pull/361
- https://github.com/hashicorp/go-getter/commit/38e97387488f5439616be60874979433a12edb48
- https://github.com/hashicorp/go-getter/commit/a2ebce998f8d4105bd4b78d6c99a12803ad97a45
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-13-multiple-vulnerabilities-in-go-getter-library
- https://discuss.hashicorp.com/t/hcsec-2022-13-multiple-vulnerabilities-in-go-getter-library/39930
- https://github.com/hashicorp/go-getter
- https://github.com/hashicorp/go-getter/releases
- https://pkg.go.dev/vuln/GO-2022-0586

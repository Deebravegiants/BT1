# [C] LZ4 vulnerable to Out-of-bounds Write

## Summary
Severity: Critical
Advisory: GHSA-4wp2-8rm2-jgmh
CVE: CVE-2014-125026
CWE: CWE-787
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-4wp2-8rm2-jgmh
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/golz4` — affected >=0 <0.0.0-20140711154735-199f5f787806

## Details
LZ4 bindings use a deprecated C API that is vulnerable to memory corruption, which could lead to arbitrary code execution if called with untrusted user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125026
- https://github.com/cloudflare/golz4/issues/5
- https://github.com/cloudflare/golz4/commit/199f5f7878062ca17a98e079f2dbe1205e2ed898
- https://github.com/cloudflare/golz4
- https://pkg.go.dev/vuln/GO-2020-0022

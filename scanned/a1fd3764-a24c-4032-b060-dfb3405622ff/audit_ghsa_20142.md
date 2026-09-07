# [H] Macaron csrf missing encryption and has sensitive cookies in HTTP session without secure attribute

## Summary
Severity: High
Advisory: GHSA-hhxg-px5h-jc32
CVE: CVE-2018-25060
CWE: CWE-311, CWE-614
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-hhxg-px5h-jc32
Type: github-advisory

## Affected
- Go: `github.com/go-macaron/csrf` — affected >=0 <0.0.0-20180426211050-dadd1711a617

## Details
A vulnerability was found in Macaron csrf and classified as problematic. Affected by this issue is some unknown functionality of the file `csrf.go`. The manipulation of the argument Generate leads to sensitive cookie without secure attribute. The attack may be launched remotely. The name of the patch is dadd1711a617000b70e5e408a76531b73187031c. It is recommended to apply a patch to fix this issue. VDB-217058 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25060
- https://github.com/go-macaron/csrf/pull/7
- https://github.com/go-macaron/csrf/commit/dadd1711a617000b70e5e408a76531b73187031c
- https://github.com/go-macaron/csrf
- https://pkg.go.dev/vuln/GO-2022-1213
- https://vuldb.com/?ctiid.217058
- https://vuldb.com/?id.217058

# [C] gosqljson SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-g7mw-9pf9-p2pm
CVE: CVE-2014-125064
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-07
Source: https://github.com/advisories/GHSA-g7mw-9pf9-p2pm
Type: github-advisory

## Affected
- Go: `github.com/elgs/gosqljson` — affected >=0 <0.0.0-20220916234230-750f26ee23c7

## Details
A vulnerability, which was classified as critical, has been found in elgs gosqljson. This issue affects the function `QueryDbToArray/QueryDbToMap/ExecDb` of the file `gosqljson.go`. The manipulation of the argument sqlStatement leads to sql injection. The name of the patch is 2740b331546cb88eb61771df4c07d389e9f0363a. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-217631.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125064
- https://github.com/elgs/gosqljson/commit/2740b331546cb88eb61771df4c07d389e9f0363a
- https://github.com/elgs/gosqljson
- https://pkg.go.dev/vuln/GO-2023-1494
- https://vuldb.com/?ctiid.217631
- https://vuldb.com/?id.217631

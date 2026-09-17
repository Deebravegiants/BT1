# [M] pastebinit Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cwh7-28vg-jmpr
CVE: CVE-2018-25059
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-cwh7-28vg-jmpr
Type: github-advisory

## Affected
- Go: `github.com/jessfraz/pastebinit` — affected >=0 <0.2.3

## Details
A vulnerability was found in pastebinit up to 0.2.2 and classified as problematic. Affected by this issue is the function pasteHandler of the file server.go. The manipulation of the argument `r.URL.Path` leads to path traversal. Upgrading to version 0.2.3 can address this issue. The name of the patch is 1af2facb6d95976c532b7f8f82747d454a092272. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-217040.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25059
- https://github.com/jessfraz/pastebinit/pull/3
- https://github.com/jessfraz/pastebinit/commit/1af2facb6d95976c532b7f8f82747d454a092272
- https://github.com/jessfraz/pastebinit
- https://github.com/jessfraz/pastebinit/releases/tag/v0.2.3
- https://vuldb.com/?ctiid.217040
- https://vuldb.com/?id.217040

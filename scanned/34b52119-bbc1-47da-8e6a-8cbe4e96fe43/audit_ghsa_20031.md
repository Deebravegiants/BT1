# [M] Macaron i18n Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jwrv-x6rx-8vfm
CVE: CVE-2020-36627
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-jwrv-x6rx-8vfm
Type: github-advisory

## Affected
- Go: `github.com/go-macaron/i18n` — affected >=0 <0.5.0

## Details
A vulnerability was found in Macaron i18n. It has been declared as problematic. Affected by this vulnerability is an unknown functionality of the file i18n.go. The manipulation leads to open redirect. The attack can be launched remotely. Upgrading to version 0.5.0 can address this issue. The name of the patch is 329b0c4844cc16a5a253c011b55180598e707735. It is recommended to upgrade the affected component. The identifier VDB-216745 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36627
- https://github.com/go-macaron/i18n/commit/329b0c4844cc16a5a253c011b55180598e707735
- https://github.com/go-macaron/i18n
- https://github.com/go-macaron/i18n/releases/tag/v0.5.0
- https://pkg.go.dev/vuln/GO-2022-1187
- https://vuldb.com/?id.216745

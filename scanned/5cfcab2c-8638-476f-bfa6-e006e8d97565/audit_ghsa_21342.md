# [C] Gogs vulnerable to Cross-site Scripting

## Summary
Severity: Critical
Advisory: GHSA-mcjj-2fvq-mc3r
CVE: CVE-2022-32174
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-mcjj-2fvq-mc3r
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0.6.5

## Details
In Gogs, versions v0.6.5 through v0.12.10 are vulnerable to Stored Cross-Site Scripting (XSS) that leads to an account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32174
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/v0.12.10/public/js/gogs.js#L263
- https://pkg.go.dev/vuln/GO-2022-1060
- https://www.mend.io/vulnerability-database/CVE-2022-32174

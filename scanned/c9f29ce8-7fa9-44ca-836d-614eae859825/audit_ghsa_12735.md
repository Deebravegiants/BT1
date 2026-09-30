# [C] Squalor SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3hc7-2xcc-7p8f
CVE: CVE-2020-36645
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-07
Source: https://github.com/advisories/GHSA-3hc7-2xcc-7p8f
Type: github-advisory

## Affected
- Go: `github.com/square/squalor` — affected >=0 <0.0.0-20200306154055-f6f0a47cc344

## Details
A vulnerability, which was classified as critical, was found in square squalor. This affects an unknown part. The manipulation leads to sql injection. Upgrading to version v0.0.0 is able to address this issue. The name of the patch is f6f0a47cc344711042eb0970cb423e6950ba3f93. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-217623.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36645
- https://github.com/square/squalor/pull/76
- https://github.com/square/squalor/commit/f6f0a47cc344711042eb0970cb423e6950ba3f93
- https://github.com/square/squalor
- https://github.com/square/squalor/releases/tag/v0.0.0
- https://vuldb.com/?ctiid.217623
- https://vuldb.com/?id.217623

# [M] AdGuardHome vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-mwwc-3jv2-62j3
CVE: CVE-2022-32175
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-mwwc-3jv2-62j3
Type: github-advisory

## Affected
- Go: `github.com/AdguardTeam/AdGuardHome` — affected >=0.95 <0.108.0-b.16

## Details
In AdGuardHome, versions v0.95 through v0.108.0-b.13 are vulnerable to Cross-Site Request Forgery (CSRF), in the custom filtering rules functionality. An attacker can persuade an authorized user to follow a malicious link, resulting in deleting/modifying the custom filtering rules.

The file that contains the vulnerable code is no longer present as of v0.108.0-b.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32175
- https://github.com/AdguardTeam/AdGuardHome/commit/756b14a61de138889130c239406dae43f1f115cb
- https://github.com/AdguardTeam/AdGuardHome
- https://github.com/AdguardTeam/AdGuardHome/blob/v0.108.0-b.13/internal/home/controlfiltering.go#L265
- https://github.com/AdguardTeam/AdGuardHome/blob/v0.108.0-b.15/internal/home/controlfiltering.go
- https://github.com/AdguardTeam/AdGuardHome/blob/v0.108.0-b.16/internal/home/controlfiltering.go
- https://www.mend.io/vulnerability-database/CVE-2022-32175

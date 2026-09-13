# [C] Grafana vulnerable to Authentication Bypass by Spoofing

## Summary
Severity: Critical
Advisory: GHSA-mpv3-g8m3-3fjc
CVE: CVE-2023-3128
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-mpv3-g8m3-3fjc
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.4.0 <9.4.13
- Go: `github.com/grafana/grafana` — affected >=9.3.0 <9.3.16
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.2.20
- Go: `github.com/grafana/grafana` — affected >=0 <8.5.27

## Details
Grafana is validating Azure AD accounts based on the email claim. 

On Azure AD, the profile email field is not unique and can be easily modified. 

This leads to account takeover and authentication bypass when Azure AD OAuth is configured with a multi-tenant app.

## References
- https://github.com/grafana/bugbounty/security/advisories/GHSA-gxh2-6vvc-rrgp
- https://nvd.nist.gov/vuln/detail/CVE-2023-3128
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/blob/69fc4e6bc0be2a82085ab3885c2262a4d49e97d8/CHANGELOG.md
- https://grafana.com/security/security-advisories/cve-2023-3128
- https://security.netapp.com/advisory/ntap-20230714-0004

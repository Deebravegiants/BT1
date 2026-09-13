# [H] Mattermost doesn't sanitize sensitive configuration fields before including them in support packet generation

## Summary
Severity: High
Advisory: GHSA-9p64-jpc7-m2rp
CVE: CVE-2026-6346
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-9p64-jpc7-m2rp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260326202606-fac92f4a71f3
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260326202606-fac92f4a71f3

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to sanitize sensitive configuration fields before including them in support packet generation, which allows a Mattermost System Admin or any party with access to a support packet to obtain sensitive credentials in plaintext via downloading a support packet from the System Console.. Mattermost Advisory ID: MMSA-2026-00607

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6346
- https://github.com/mattermost/mattermost/commit/fac92f4a71f356009e27983a980f729f599e8ba5
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

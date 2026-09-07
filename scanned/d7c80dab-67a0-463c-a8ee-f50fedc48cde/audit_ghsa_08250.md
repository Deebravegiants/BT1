# [M] Mattermost doesn't validate 7zip archive structure before processing

## Summary
Severity: Medium
Advisory: GHSA-cjm8-jxpw-g43m
CVE: CVE-2026-6340
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-cjm8-jxpw-g43m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260325191733-fb11968f8798
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260325191733-fb11968f8798

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to validate 7zip archive structure before processing which allows an authenticated attacker to cause server memory exhaustion and denial of service via uploading a specially crafted 7zip file with excessive folder declarations.. Mattermost Advisory ID: MMSA-2026-00573

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6340
- https://github.com/mattermost/mattermost/commit/fb11968f8798925c7b75711025bc5f991124ba26
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

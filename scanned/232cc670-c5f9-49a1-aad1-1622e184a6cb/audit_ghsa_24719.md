# [C] Mattermost Server has X.509 Improper Certificate Validation

## Summary
Severity: Critical
Advisory: GHSA-m462-mqw4-2c8m
CVE: CVE-2017-18911
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m462-mqw4-2c8m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.6.7-rc1
- Go: `github.com/mattermost/mattermost-server` — affected >=3.7.0 <3.7.5
- Go: `github.com/mattermost/mattermost-server` — affected >=3.8.0 <3.8.2

## Details
An issue was discovered in Mattermost Server before 3.8.2, 3.7.5, and 3.6.7. The X.509 certificate validation can be skipped for a TLS-based e-mail server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18911
- https://github.com/mattermost/mattermost/commit/222bce0c5c1abb2f58c3a6de1fe8c5d3accffb21
- https://github.com/mattermost/mattermost/commit/691c18157025d4808b5b11de1d6de01050e54fa6
- https://github.com/mattermost/mattermost/commit/e9bb8cdfb4915067349a4840ab15ff941c4eb070
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

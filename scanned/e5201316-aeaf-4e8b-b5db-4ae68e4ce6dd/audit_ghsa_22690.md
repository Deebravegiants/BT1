# [H] Mattermost Server SAML implementation does not require encryption or signature verification as default

## Summary
Severity: High
Advisory: GHSA-r6j5-fqx9-7qv9
CVE: CVE-2017-18909
CWE: CWE-311, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r6j5-fqx9-7qv9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.8.1-0.20170504181128-4f074fed0d65

## Details
An issue was discovered in Mattermost Server before 3.9.0 when SAML is used. Encryption and signature verification are not mandatory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18909
- https://github.com/mattermost/mattermost/commit/4f074fed0d653a28779ac586e418341232d43e95
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

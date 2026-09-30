# [C] Mattermost allows unsolicited invites to expose access to local channels

## Summary
Severity: Critical
Advisory: GHSA-q22q-2rrf-m27p
CVE: CVE-2024-39777
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-q22q-2rrf-m27p
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.1

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5 and 9.8.x <= 9.8.1 fail to disallow unsolicited invites to expose access to local channels, when shared channels are enabled, which allows a malicious remote to send an invite with the ID of an existing local channel, and that local channel will then become shared without the consent of the local admin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39777
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

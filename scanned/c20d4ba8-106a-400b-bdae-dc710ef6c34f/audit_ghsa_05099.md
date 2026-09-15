# [M] Mattermost doesn't enforce PermissionInviteUser when setting AllowOpenInvite or AllowedDomains during team creation

## Summary
Severity: Medium
Advisory: GHSA-c28q-m4gf-vg4q
CVE: CVE-2026-6689
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-c28q-m4gf-vg4q
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.17
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250731163400-5b955468ea1e <8.0.0-20260501144115-7d6816abdfd1

## Details
Mattermost versions 11.6.x <= 11.6.1, 11.5.x <= 11.5.4, 10.11.x <= 10.11.15, 10.11.x <= 10.11.16 Fail to enforce PermissionInviteUser when setting AllowOpenInvite or AllowedDomains during team creation (the check was only applied on update/patch), which allows an authenticated user holding PermissionCreateTeam but not PermissionInviteUser on the resulting team to configure invite-controlled team settings (make the team publicly joinable via open invite and/or constrain membership via allowed domains) that they are not permitted to set on an existing team via POST /api/v4/teams with allow_open_invite: true and/or a non-empty allowed_domains in the request body.. Mattermost Advisory ID: MMSA-2026-00655

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6689
- https://github.com/mattermost/mattermost/pull/36402
- https://github.com/mattermost/mattermost/pull/36384
- https://github.com/mattermost/mattermost/pull/36383
- https://github.com/mattermost/mattermost/pull/36375
- https://github.com/mattermost/mattermost/pull/36188
- https://github.com/mattermost/mattermost/commit/977c791e5b54bc14fdb96a2b3dacc85da5d8c623
- https://github.com/mattermost/mattermost/commit/7d6816abdfd170169f717aea43c5716a1f9ef6b0
- https://github.com/mattermost/mattermost/commit/479fc42d0ec6da48e76b59608233d90bfc69769d
- https://github.com/mattermost/mattermost/commit/3a96344214b1a84df70d97052d46b6f2b40b0caa
- https://github.com/mattermost/mattermost/commit/2dea05864024b3254fb28c5ed679592e2b7cd672
- https://github.com/mattermost/mattermost/releases/tag/v10.11.16
- https://github.com/mattermost/mattermost/releases/tag/v11.5.5
- https://github.com/mattermost/mattermost/releases/tag/v11.6.2
- https://github.com/mattermost/mattermost/releases/tag/v11.7.0
- https://mattermost.com/security-updates
- https://github.com/mattermost/mattermost

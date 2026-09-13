# [H] Mattermost doesn't sanitize FileInfo.Name received from federated peers during shared channel file sync

## Summary
Severity: High
Advisory: GHSA-8qq9-cqj8-82w4
CVE: CVE-2026-6961
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-8qq9-cqj8-82w4
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.17
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250731163400-5b955468ea1e <8.0.0-20260423180926-c021eeaff8f0

## Details
Mattermost versions 11.6.x <= 11.6.1, 11.5.x <= 11.5.4, 10.11.x <= 10.11.15, 10.11.x <= 10.11.16 fail to sanitize FileInfo.Name received from federated peers during shared channel file sync, which allows an attacker who controls a federated server to write files to arbitrary locations within the target server's filestore via path traversal sequences in the filename field. Mattermost Advisory ID: MMSA-2026-00661

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6961
- https://github.com/mattermost/mattermost/pull/36255
- https://github.com/mattermost/mattermost/pull/36253
- https://github.com/mattermost/mattermost/pull/36252
- https://github.com/mattermost/mattermost/pull/36251
- https://github.com/mattermost/mattermost/pull/36223
- https://github.com/mattermost/mattermost/commit/c896a63dc44c2f9c081a0a15bfddc4e6eb50e753
- https://github.com/mattermost/mattermost/commit/c021eeaff8f003034ab40f82c552cc26a710a8fd
- https://github.com/mattermost/mattermost/commit/a9f3868e1eee9ec61855cd7277f39937385efffd
- https://github.com/mattermost/mattermost/commit/a0056ed68d95f64d7c4586985e7b7f16b96b3bec
- https://github.com/mattermost/mattermost/commit/61d68d2d6ee81a5919597d91c736c502d7156859
- https://github.com/mattermost/mattermost/releases/tag/v10.11.16
- https://github.com/mattermost/mattermost/releases/tag/v11.5.5
- https://github.com/mattermost/mattermost/releases/tag/v11.6.2
- https://github.com/mattermost/mattermost/releases/tag/v11.7.0
- https://mattermost.com/security-updates
- https://github.com/mattermost/mattermost

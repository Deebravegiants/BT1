# [M] Mattermost doesn't require system-level permission when patching protected default system roles

## Summary
Severity: Medium
Advisory: GHSA-m2w9-h2mm-79qr
CVE: CVE-2026-6739
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-m2w9-h2mm-79qr
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.17
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250731163400-5b955468ea1e <8.0.0-20260501142004-99b73d4c4acf

## Details
Mattermost versions 11.6.x <= 11.6.1, 11.5.x <= 11.5.4, 10.11.x <= 10.11.15, 10.11.x <= 10.11.16 fail to require system-level permission when patching protected default system roles, which allows authenticated users with delegated user-management permissions to escalate privileges by altering built-in role permissions via the role patch API. Mattermost Advisory ID: MMSA-2026-00656

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6739
- https://github.com/mattermost/mattermost/pull/36197
- https://github.com/mattermost/mattermost/pull/36377
- https://github.com/mattermost/mattermost/pull/36379
- https://github.com/mattermost/mattermost/pull/36380
- https://github.com/mattermost/mattermost/pull/36382
- https://github.com/mattermost/mattermost/commit/2c89c2f6768fbe4dfd57a21ca38c0aecead8d4a8
- https://github.com/mattermost/mattermost/commit/5e159647b16e571b327ac6882f32eae42971f540
- https://github.com/mattermost/mattermost/commit/8000e5933526f4fd66b92131db3a1b1f4520dbae
- https://github.com/mattermost/mattermost/commit/f0a390b96e4c730daedbaf5190684776730218c7
- https://github.com/mattermost/mattermost
- https://github.com/mattermost/mattermost/releases/tag/v10.11.16
- https://github.com/mattermost/mattermost/releases/tag/v11.5.5
- https://github.com/mattermost/mattermost/releases/tag/v11.6.2
- https://github.com/mattermost/mattermost/releases/tag/v11.7.0
- https://mattermost.com/security-updates

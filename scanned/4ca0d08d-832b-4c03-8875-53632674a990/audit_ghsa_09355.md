# [M] Mattermost doesn't validate the response body of proxied images

## Summary
Severity: Medium
Advisory: GHSA-j76w-p754-g2w7
CVE: CVE-2026-4054
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-j76w-p754-g2w7
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost-server` — affected >=0.0.0-20250731163400-5b955468ea1e <0.0.0-20260414103857-b21ef302025e
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.4

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to validate the response body of proxied images, which allows a remote attacker to enact client-side DoS via an SVG file served from an attacker-controlled origin under a non-SVG Content-Type header (e.g. image/png) embedded in an og:image meta tag or Markdown image link. Mattermost Advisory ID: MMSA-2026-00630.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4054
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

# [M] Mattermost doesn't validate the TIFF IFD offset in the image header before allocating memory

## Summary
Severity: Medium
Advisory: GHSA-37j2-3vv8-cf24
CVE: CVE-2026-5755
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-37j2-3vv8-cf24
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.2, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to validate the TIFF IFD offset in the image header before allocating memory, which allows authenticated users with file upload or posting permissions to cause a denial of service (server OOM) via uploading a crafted TIFF file or posting a URL that serves one.. Mattermost Advisory ID: MMSA-2026-00648

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5755
- https://github.com/mattermost/mattermost/commit/d37c2d9d50b50963dabd92153adf7ed52016769a
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

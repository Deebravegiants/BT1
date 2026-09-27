# [M] Mattermost subject to Denial of Service via upload of special GIF

## Summary
Severity: Medium
Advisory: GHSA-m7w4-q5vg-5xfp
CVE: CVE-2022-3257
CWE: CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-m7w4-q5vg-5xfp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.1.0 <7.2.0

## Details
Mattermost version 7.1.x and earlier fails to sufficiently process a specifically crafted GIF file when it is uploaded while drafting a post, which allows authenticated users to cause resource exhaustion while processing the file, resulting in server-side Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3257
- https://hackerone.com/reports/1620170
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates

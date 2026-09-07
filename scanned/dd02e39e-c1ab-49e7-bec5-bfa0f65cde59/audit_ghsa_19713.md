# [M] Mattermost Fails to Properly Perform Viewer Role Authorization

## Summary
Severity: Medium
Advisory: GHSA-fqrq-xmxj-v47x
CVE: CVE-2025-1472
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-fqrq-xmxj-v47x
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.9

## Details
Mattermost versions 9.11.x <= 9.11.8 fail to properly perform authorization of the Viewer role which allows an attacker with the Viewer role configured with No Access to Reporting to still view team and site statistics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1472
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates

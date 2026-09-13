# [H] Mattermost Microsoft Teams Plugin fails to properly mask sensitive configuration values

## Summary
Severity: High
Advisory: GHSA-4ppj-6chv-5pgc
CVE: CVE-2026-2476
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-4ppj-6chv-5pgc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-msteams` — affected >=0 <1.15.1-0.20260102165339-036c761bd3cb

## Details
Mattermost Plugins versions <=2.0.3.0 fail to properly mask sensitive configuration values which allows an attacker with access to support packets to obtain original plugin settings via exported configuration data. Mattermost Advisory ID: MMSA-2026-00606

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2476
- https://github.com/mattermost/mattermost-plugin-msteams/commit/036c761bd3cb9ece92c17f2b151dfa906cebdcf6
- https://github.com/mattermost/mattermost-plugin-msteams
- https://mattermost.com/security-updates

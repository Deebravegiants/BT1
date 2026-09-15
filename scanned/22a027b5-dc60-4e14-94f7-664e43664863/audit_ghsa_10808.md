# [M] Mattermost Boards Plugin fails to implement authorisation checks on comment block modifications

## Summary
Severity: Medium
Advisory: GHSA-hf8w-x9h5-5gf9
CVE: CVE-2026-2461
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-hf8w-x9h5-5gf9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-boards` — affected >=0 <0.0.0-20260108044135-57c5be5b6ef5

## Details
Mattermost Plugins versions <=11.3 11.0.3 11.2.2 10.10.11.0 fail to implement authorisation checks on comment block modifications, which allows an authorised attacker with editor permission to modify comments created by other board members.  Mattermost Advisory ID: MMSA-2025-00559

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2461
- https://github.com/mattermost/mattermost-plugin-boards/commit/57c5be5b6ef59d02dd72e35094d1fae8ba6e9619
- https://github.com/mattermost/mattermost-plugin-boards
- https://mattermost.com/security-updates

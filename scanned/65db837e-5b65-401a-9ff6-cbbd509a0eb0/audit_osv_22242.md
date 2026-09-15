# [M] Malicious imports can lead to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2022-2406
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-07-14
Source: https://osv.dev/vulnerability/CVE-2022-2406
Type: osv

## Details
The legacy Slack import feature in Mattermost version 6.7.0 and earlier fails to properly limit the sizes of imported files, which allows an authenticated attacker to crash the server by importing large files via the Slack import REST API.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2406.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2406

# [M] IDOR in Jira plugin subscription edit endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-6062
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-6062
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.0, 11.6.x <= 11.6.2, 11.5.x <= 11.5.5, 10.11.x <= 10.11.17 Fail to validate channel ownership of an existing subscription before applying edits which allows an authenticated attacker to hijack subscriptions from channels they have no access to via a crafted PUT request to the subscription edit endpoint.. Mattermost Advisory ID: MMSA-2026-00650

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6062.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-6062

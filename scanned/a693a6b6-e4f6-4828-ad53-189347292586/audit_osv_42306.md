# [M] Mattermost Jira plugin had unauthenticated {{/ac/installed}} lifecycle callback during pending Jira Cloud install

## Summary
Severity: Medium
Advisory: CVE-2026-6673
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-6673
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.0, 11.6.x <= 11.6.2, 11.5.x <= 11.5.5, 10.11.x <= 10.11.17 fail to authenticate Atlassian Connect installed callbacks, allowing a remote unauthenticated attacker to inject a rogue sharedSecret and disrupt the Jira integration via POST to /ac/installed during the pending-install window.. Mattermost Advisory ID: MMSA-2026-00654

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6673.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-6673

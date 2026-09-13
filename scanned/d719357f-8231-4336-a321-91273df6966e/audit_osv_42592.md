# [M] Crafted message attachment causes client-side denial of service via markdown parser regex backtracking in Mattermost

## Summary
Severity: Medium
Advisory: CVE-2026-6850
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-6850
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to validate the length and content of message attachment field values, which allows an authenticated attacker to cause a denial of service for all users in a channel via a post containing a specially crafted payload that triggers catastrophic backtracking in the client-side markdown parser.. Mattermost Advisory ID: MMSA-2026-00658

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6850.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-6850

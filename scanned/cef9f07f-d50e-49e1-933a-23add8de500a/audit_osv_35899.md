# [M] Permalink Preview Information Disclosure After Permission Revocation

## Summary
Severity: Medium
Advisory: CVE-2026-1629
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-1629
Type: osv

## Details
Mattermost versions 10.11.x <= 10.11.10 Fail to invalidate cached permalink preview data when a user loses channel access which allows the user to continue viewing private channel content via previously cached permalink previews until cache reset or relogin.. Mattermost Advisory ID: MMSA-2026-00580

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1629.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-1629

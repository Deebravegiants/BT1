# [M] Mobile SSO authentication flow allows credential theft via malicious server

## Summary
Severity: Medium
Advisory: CVE-2026-22880
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-22880
Type: osv

## Details
Mattermost Mobile Apps versions <=2.37 11.4 2.0.37 11.0.4 11.1.3 11.3.2 10.11.11.0 fail to properly validate the SSO authentication callback origin which allows an attacker controlling a malicious Mattermost server to steal user credentials for a legitimate Mattermost server via relaying the SSO code exchange flow through the mobile application. Mattermost Advisory ID: MMSA-2025-00564

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22880.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-22880

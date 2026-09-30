# [M] Deactivated guest accounts can authenticate via magic-link token in Mattermost REST API login endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-9597
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-9597
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4 fail to verify whether a guest account is deactivated before creating a session in the magic-link token login path, which allows a deactivated guest user to obtain a fully functional session via a magic-link token issued prior to deactivation.. Mattermost Advisory ID: MMSA-2026-00681

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9597.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9597

# [H] Domain Restriction Bypass on Registration

## Summary
Severity: High
Advisory: CVE-2024-11599
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-11-28
Source: https://osv.dev/vulnerability/CVE-2024-11599
Type: osv

## Details
Mattermost versions 10.0.x <= 10.0.1, 10.1.x <= 10.1.1, 9.11.x <= 9.11.3, 9.5.x <= 9.5.11 fail to properly validate email addresses which allows an unauthenticated user to bypass email domain restrictions via carefully crafted input on email registration.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11599.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11599

# [H] SuiteCRM: Privilege Escalation via Improper Session Invalidation and Inactive User Bypass

## Summary
Severity: High
Advisory: CVE-2025-64489
Aliases: GHSA-j6jg-9jj3-q2ph
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-11-08
Source: https://osv.dev/vulnerability/CVE-2025-64489
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Versions 7.14.7 and prior, 8.0.0-beta.1 through 8.9.0 contain a privilege escalation vulnerability where user sessions are not invalidated upon account deactivation. An inactive user with an active session can continue to access the application and, critically, can self-reactivate their account. This undermines administrative controls and allows unauthorized persistence. This issue is fixed in versions 7.14.8 and 8.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64489.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-j6jg-9jj3-q2ph
- https://nvd.nist.gov/vuln/detail/CVE-2025-64489
- https://github.com/SuiteCRM/SuiteCRM-Core/commit/30277cfe69755f7360a23d4805e06a5c38f14131
- https://github.com/SuiteCRM/SuiteCRM/commit/40da2845a170832a4e9e9fa0ebe731f8c34de42d

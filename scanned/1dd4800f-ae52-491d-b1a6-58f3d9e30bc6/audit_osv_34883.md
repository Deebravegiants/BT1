# [C] FreePBX Endpoint Manager Allows Unauthenticated Logins to Administrator Control Panel via Forged Basic Auth Header

## Summary
Severity: Critical
Advisory: CVE-2025-66039
Aliases: GHSA-9jvh-mv6x-w698
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-66039
Type: osv

## Details
FreePBX Endpoint Manager is a module for managing telephony endpoints in FreePBX systems. Versions are vulnerable to authentication bypass when the authentication type is set to "webserver." When providing an Authorization header with an arbitrary value, a session is associated with the target user regardless of valid credentials. This issue is fixed in versions 16.0.44 and 17.0.23.

## References
- https://www.freepbx.org/watch-what-we-do-with-security-fixes-%f0%9f%91%80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66039.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-9jvh-mv6x-w698
- https://nvd.nist.gov/vuln/detail/CVE-2025-66039
- https://github.com/FreePBX/framework/commit/04224253156543cd9932b90458660b2f19fc0e35#diff-72f14a52840a61504a8e03cd195035b44e488aecd634b001bc6412a04bdc940bR20-R50

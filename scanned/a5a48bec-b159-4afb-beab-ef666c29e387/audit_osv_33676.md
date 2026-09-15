# [M] FreeScout Has Business Logic Errors

## Summary
Severity: Medium
Advisory: CVE-2025-48476
Aliases: GHSA-7h5m-q39p-h849
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2025-48476
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.180, when adding and editing user records using the fill() method, there is no check for the absence of the password field in the data coming from the user, which leads to a mass-assignment vulnerability. As a result, a user with the right to edit other users of the system can change their password, and then log in to the system using the set password. This issue has been patched in version 1.8.180.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48476.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-7h5m-q39p-h849
- https://nvd.nist.gov/vuln/detail/CVE-2025-48476

# [C] filebrowser through 2.63.16 Privilege Escalation via Signup

## Summary
Severity: Critical
Advisory: CVE-2026-72839
Aliases: GHSA-6759-996p-gpj6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72839
Type: osv

## Details
filebrowser through 2.63.16 fails to properly restrict scope and permissions when self-signup is enabled with default CreateUserDir setting. Unauthenticated attackers can register accounts that inherit the server root scope with full create, modify, delete, rename, share, and download permissions, allowing unrestricted access to all files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72839.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-6759-996p-gpj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-72839
- https://www.vulncheck.com/advisories/filebrowser-through-privilege-escalation-via-signup

# [H] Authenticated SQL Injection in Contact/query addressBookIds filter

## Summary
Severity: High
Advisory: CVE-2026-33755
Aliases: GHSA-3gc4-5993-c2qc
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33755
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Prior to versions 6.8.158, 25.0.92, and 26.0.17, an authenticated SQL Injection vulnerability in the JMAP `Contact/query` endpoint allows any authenticated user with basic addressbook access to extract arbitrary data from the database — including active session tokens of other users. This enables full account takeover of any user, including the System Administrator, without knowing their password. Versions 6.8.158, 25.0.92, and 26.0.17 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33755.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-3gc4-5993-c2qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33755
